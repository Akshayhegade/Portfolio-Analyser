import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../../App';

// Mock the child components to focus on App.js functionality
jest.mock('../../components/AssetList', () => {
  return function MockAssetList({ assets, onDeleteAsset, onUpdateAsset, onBulkDeleteAssets }) {
    return (
      <div data-testid="mock-asset-list">
        <button onClick={() => onDeleteAsset('1')}>Mock Delete Asset</button>
        <button onClick={() => onUpdateAsset('1', { symbol: 'TEST', asset_type: 'Indian Stock', purchase_price: 1000, quantity: 10, purchase_date: '2023-01-01' })}>
          Mock Update Asset
        </button>
        <button onClick={() => onBulkDeleteAssets(['1', '2'])}>Mock Bulk Delete</button>
        <div>Asset Count: {assets.length}</div>
      </div>
    );
  };
});

jest.mock('../../components/AddAssetForm', () => {
  return function MockAddAssetForm({ onAddAsset, onClose }) {
    return (
      <div data-testid="mock-add-asset-form">
        <button onClick={() => onAddAsset({ symbol: 'NEW', asset_type: 'Indian Stock', purchase_price: 1000, quantity: 10, purchase_date: '2023-01-01' })}>
          Mock Add Asset
        </button>
        <button onClick={onClose}>Mock Close</button>
      </div>
    );
  };
});

jest.mock('../../components/PortfolioCharts', () => {
  return function MockPortfolioCharts() {
    return <div data-testid="mock-portfolio-charts">Mock Portfolio Charts</div>;
  };
});

// Mock fetch API
global.fetch = jest.fn();

describe('App Component', () => {
  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
    
    // Mock successful fetch for assets
    global.fetch.mockImplementation((url) => {
      if (url.includes('/assets')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([
            { id: '1', symbol: 'TEST1', asset_type: 'Indian Stock', purchase_price: 1000, quantity: 10, purchase_date: '2023-01-01' },
            { id: '2', symbol: 'TEST2', asset_type: 'US Stock', purchase_price: 2000, quantity: 5, purchase_date: '2023-02-01' }
          ])
        });
      }
      
      // Mock prices endpoint
      if (url.includes('/prices')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            'TEST1': 1100,
            'TEST2': 2200
          })
        });
      }
      
      return Promise.reject(new Error('Unhandled fetch URL'));
    });
  });

  test('renders main components', async () => {
    render(<App />);
    
    // Wait for assets to load
    await waitFor(() => {
      expect(screen.getByTestId('mock-portfolio-charts')).toBeInTheDocument();
      expect(screen.getByTestId('mock-asset-list')).toBeInTheDocument();
    });
    
    // Add Asset button should be visible
    expect(screen.getByText(/add asset/i)).toBeInTheDocument();
  });

  test('handles adding an asset', async () => {
    // Mock successful POST response for adding an asset
    global.fetch.mockImplementationOnce((url, options) => {
      if (url.includes('/assets') && options.method === 'POST') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ id: '3', symbol: 'NEW', asset_type: 'Indian Stock', purchase_price: 1000, quantity: 10, purchase_date: '2023-01-01' })
        });
      }
      return Promise.reject(new Error('Unhandled fetch URL'));
    });
    
    render(<App />);
    
    // Open Add Asset form
    fireEvent.click(screen.getByText(/add asset/i));
    
    // Add Asset form should be visible
    await waitFor(() => {
      expect(screen.getByTestId('mock-add-asset-form')).toBeInTheDocument();
    });
    
    // Submit the form
    fireEvent.click(screen.getByText('Mock Add Asset'));
    
    // Verify fetch was called with correct parameters
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/assets'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
          body: expect.any(String)
        })
      );
    });
  });

  test('handles deleting an asset', async () => {
    // Mock successful DELETE response
    global.fetch.mockImplementationOnce((url, options) => {
      if (url.includes('/assets/1') && options.method === 'DELETE') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ message: 'Asset deleted successfully' })
        });
      }
      return Promise.reject(new Error('Unhandled fetch URL'));
    });
    
    render(<App />);
    
    // Wait for assets to load
    await waitFor(() => {
      expect(screen.getByTestId('mock-asset-list')).toBeInTheDocument();
    });
    
    // Click delete button
    fireEvent.click(screen.getByText('Mock Delete Asset'));
    
    // Verify fetch was called with correct parameters
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/assets/1'),
        expect.objectContaining({
          method: 'DELETE'
        })
      );
    });
  });

  test('handles updating an asset', async () => {
    // Mock successful PUT response
    global.fetch.mockImplementationOnce((url, options) => {
      if (url.includes('/assets/1') && options.method === 'PUT') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ 
            id: '1', 
            symbol: 'TEST', 
            asset_type: 'Indian Stock', 
            purchase_price: 1000, 
            quantity: 10, 
            purchase_date: '2023-01-01' 
          })
        });
      }
      return Promise.reject(new Error('Unhandled fetch URL'));
    });
    
    render(<App />);
    
    // Wait for assets to load
    await waitFor(() => {
      expect(screen.getByTestId('mock-asset-list')).toBeInTheDocument();
    });
    
    // Click update button
    fireEvent.click(screen.getByText('Mock Update Asset'));
    
    // Verify fetch was called with correct parameters
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/assets/1'),
        expect.objectContaining({
          method: 'PUT',
          headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
          body: expect.any(String)
        })
      );
    });
  });

  test('handles bulk deleting assets', async () => {
    // Mock successful bulk DELETE response
    global.fetch.mockImplementationOnce((url, options) => {
      if (url.includes('/assets') && options.method === 'DELETE') {
        const body = JSON.parse(options.body);
        if (body.ids && Array.isArray(body.ids)) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ message: `${body.ids.length} assets deleted successfully` })
          });
        }
      }
      return Promise.reject(new Error('Unhandled fetch URL'));
    });
    
    render(<App />);
    
    // Wait for assets to load
    await waitFor(() => {
      expect(screen.getByTestId('mock-asset-list')).toBeInTheDocument();
    });
    
    // Click bulk delete button
    fireEvent.click(screen.getByText('Mock Bulk Delete'));
    
    // Verify fetch was called with correct parameters
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringMatching(/\/assets$/), // Should end with /assets (no trailing slash)
        expect.objectContaining({
          method: 'DELETE',
          headers: expect.objectContaining({ 
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }),
          body: JSON.stringify({ ids: ['1', '2'] })
        })
      );
    });
  });

  test('handles API errors gracefully', async () => {
    // Mock failed fetch for assets
    global.fetch.mockImplementationOnce(() => {
      return Promise.resolve({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ error: 'Server error' })
      });
    });
    
    render(<App />);
    
    // Error message should be displayed
    await waitFor(() => {
      expect(screen.getByText(/failed to load assets/i)).toBeInTheDocument();
    });
  });
});
