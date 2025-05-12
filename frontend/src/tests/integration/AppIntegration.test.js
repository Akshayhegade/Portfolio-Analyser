import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../../App';

// Mock fetch API for integration tests
global.fetch = jest.fn();

// Mock data
const mockAssets = [
  { id: '1', symbol: 'RELIANCE.NS', asset_type: 'Indian Stock', purchase_price: 2500, quantity: 10, purchase_date: '2023-01-15' },
  { id: '2', symbol: 'INFY.NS', asset_type: 'Indian Stock', purchase_price: 1500, quantity: 20, purchase_date: '2023-02-20' },
  { id: '3', symbol: 'AAPL', asset_type: 'US Stock', purchase_price: 15000, quantity: 5, purchase_date: '2023-03-10' },
  { id: '4', symbol: 'BTC', asset_type: 'Crypto', purchase_price: 2500000, quantity: 0.05, purchase_date: '2023-04-05' }
];

const mockPrices = {
  'RELIANCE.NS': 2700,
  'INFY.NS': 1600,
  'AAPL': 16000,
  'BTC': 2700000
};

// Mock LivePriceInfo component to avoid actual API calls
jest.mock('../../components/LivePriceInfo', () => {
  return function MockLivePriceInfo({ asset }) {
    return (
      <div data-testid={`live-price-${asset.symbol}`}>
        Live Price: {mockPrices[asset.symbol] || 'N/A'}
      </div>
    );
  };
});

describe('App Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock successful fetch for assets
    global.fetch.mockImplementation((url, options) => {
      // GET assets
      if (url.includes('/assets') && (!options || options.method === 'GET' || !options.method)) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([...mockAssets])
        });
      }
      
      // POST new asset
      if (url.includes('/assets') && options && options.method === 'POST') {
        const newAsset = JSON.parse(options.body);
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ id: '5', ...newAsset })
        });
      }
      
      // DELETE single asset
      if (url.match(/\/assets\/[a-zA-Z0-9-]+$/) && options && options.method === 'DELETE') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ message: 'Asset deleted successfully' })
        });
      }
      
      // PUT update asset
      if (url.match(/\/assets\/[a-zA-Z0-9-]+$/) && options && options.method === 'PUT') {
        const updatedAsset = JSON.parse(options.body);
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ id: url.split('/').pop(), ...updatedAsset })
        });
      }
      
      // Bulk DELETE assets
      if (url.includes('/assets') && options && options.method === 'DELETE' && options.body) {
        const { ids } = JSON.parse(options.body);
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ message: `${ids.length} assets deleted successfully` })
        });
      }
      
      // Prices endpoint
      if (url.includes('/prices')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockPrices)
        });
      }
      
      return Promise.reject(new Error(`Unhandled fetch URL: ${url}`));
    });
  });

  test('full application workflow with bulk delete', async () => {
    render(<App />);
    
    // Wait for assets to load
    await waitFor(() => {
      expect(screen.getByText('Portfolio Summary')).toBeInTheDocument();
    });
    
    // Verify Portfolio Summary is displayed
    expect(screen.getByText('Portfolio Summary')).toBeInTheDocument();
    
    // Verify Asset Management section is displayed
    const assetManagementSection = await screen.findByText('Asset Management');
    expect(assetManagementSection).toBeInTheDocument();
    
    // Wait for asset list to load
    await waitFor(() => {
      expect(screen.getByText('RELIANCE.NS')).toBeInTheDocument();
    });
    
    // Verify Indian Stocks tab is active by default and shows correct assets
    expect(screen.getByText('RELIANCE.NS')).toBeInTheDocument();
    expect(screen.getByText('INFY.NS')).toBeInTheDocument();
    
    // Test bulk delete functionality
    // First, verify no "Delete Selected" button initially
    expect(screen.queryByText(/delete selected/i)).not.toBeInTheDocument();
    
    // Select assets for deletion
    const checkboxes = screen.getAllByRole('checkbox');
    fireEvent.click(checkboxes[1]); // First asset checkbox (after select all)
    fireEvent.click(checkboxes[2]); // Second asset checkbox
    
    // Verify "Delete Selected" button appears
    const deleteSelectedButton = await screen.findByText(/delete selected \(2\)/i);
    expect(deleteSelectedButton).toBeInTheDocument();
    
    // Click "Delete Selected" button
    fireEvent.click(deleteSelectedButton);
    
    // Verify bulk delete API was called correctly
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringMatching(/\/assets$/),
        expect.objectContaining({
          method: 'DELETE',
          headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
          body: expect.stringMatching(/ids/)
        })
      );
    });
    
    // Verify GET assets is called again to refresh the list
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringMatching(/\/assets$/),
        expect.any(Object)
      );
    });
    
    // Switch to US Stocks tab
    const usStocksTab = screen.getByRole('tab', { name: /us stocks/i });
    fireEvent.click(usStocksTab);
    
    // Verify US stock is displayed
    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });
    
    // Switch to Crypto tab
    const cryptoTab = screen.getByRole('tab', { name: /crypto/i });
    fireEvent.click(cryptoTab);
    
    // Verify crypto asset is displayed
    await waitFor(() => {
      expect(screen.getByText('BTC')).toBeInTheDocument();
    });
  });

  test('handles API errors gracefully', async () => {
    // Override the mock to simulate an error
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

  test('bulk delete handles errors gracefully', async () => {
    // First render with successful asset loading
    render(<App />);
    
    // Wait for assets to load
    await waitFor(() => {
      expect(screen.getByText('RELIANCE.NS')).toBeInTheDocument();
    });
    
    // Override fetch mock for the bulk delete call to simulate an error
    global.fetch.mockImplementationOnce((url, options) => {
      if (url.includes('/assets') && options && options.method === 'DELETE' && options.body) {
        return Promise.resolve({
          ok: false,
          status: 500,
          json: () => Promise.resolve({ error: 'Failed to delete assets' })
        });
      }
      return Promise.reject(new Error('Unhandled fetch URL'));
    });
    
    // Select assets for deletion
    const checkboxes = screen.getAllByRole('checkbox');
    fireEvent.click(checkboxes[1]); // First asset checkbox
    fireEvent.click(checkboxes[2]); // Second asset checkbox
    
    // Click "Delete Selected" button
    const deleteSelectedButton = await screen.findByText(/delete selected \(2\)/i);
    fireEvent.click(deleteSelectedButton);
    
    // Error message should be displayed
    await waitFor(() => {
      expect(screen.getByText(/failed to delete selected assets/i)).toBeInTheDocument();
    });
  });
});
