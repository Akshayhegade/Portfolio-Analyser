import React from 'react';
import { render, screen, fireEvent, within } from '@testing-library/react';
import '@testing-library/jest-dom';
import AssetList from '../../components/AssetList';

// Mock the LivePriceInfo component since we're only testing AssetList
jest.mock('../../components/LivePriceInfo', () => {
  return function MockLivePriceInfo() {
    return <div data-testid="mock-live-price">Live Price Mock</div>;
  };
});

describe('AssetList Component', () => {
  // Sample test data
  const mockAssets = [
    {
      id: '1',
      symbol: 'RELIANCE.NS',
      asset_type: 'Indian Stock',
      purchase_price: 2500,
      quantity: 10,
      purchase_date: '2023-01-15'
    },
    {
      id: '2',
      symbol: 'INFY.NS',
      asset_type: 'Indian Stock',
      purchase_price: 1500,
      quantity: 20,
      purchase_date: '2023-02-20'
    },
    {
      id: '3',
      symbol: 'AAPL',
      asset_type: 'US Stock',
      purchase_price: 15000,
      quantity: 5,
      purchase_date: '2023-03-10'
    }
  ];

  const mockHandlers = {
    onDeleteAsset: jest.fn(),
    onUpdateAsset: jest.fn(),
    onBulkDeleteAssets: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading spinner when loading', () => {
    render(<AssetList assets={[]} loading={true} error={null} {...mockHandlers} />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('renders error message when there is an error', () => {
    const errorMsg = 'Failed to load assets';
    render(<AssetList assets={[]} loading={false} error={errorMsg} {...mockHandlers} />);
    expect(screen.getByText(errorMsg)).toBeInTheDocument();
  });

  test('renders tabs and asset tables correctly', () => {
    render(<AssetList assets={mockAssets} loading={false} error={null} {...mockHandlers} />);
    
    // Check if tabs are rendered
    expect(screen.getByRole('tab', { name: /indian stocks/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /us stocks/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /crypto/i })).toBeInTheDocument();
    
    // Check if Indian stocks are displayed by default
    expect(screen.getByText('RELIANCE.NS')).toBeInTheDocument();
    expect(screen.getByText('INFY.NS')).toBeInTheDocument();
    
    // US Stocks should not be visible initially
    expect(screen.queryByText('AAPL')).not.toBeInTheDocument();
    
    // Switch to US Stocks tab
    fireEvent.click(screen.getByRole('tab', { name: /us stocks/i }));
    
    // Now AAPL should be visible
    expect(screen.getByText('AAPL')).toBeInTheDocument();
    // And Indian stocks should be hidden
    expect(screen.queryByText('RELIANCE.NS')).not.toBeInTheDocument();
  });

  test('single delete functionality works correctly', () => {
    render(<AssetList assets={mockAssets} loading={false} error={null} {...mockHandlers} />);
    
    // Find and click the delete button for the first asset
    const deleteButtons = screen.getAllByLabelText('delete asset');
    fireEvent.click(deleteButtons[0]);
    
    // Check if onDeleteAsset was called with the correct asset ID
    expect(mockHandlers.onDeleteAsset).toHaveBeenCalledWith('1');
  });

  test('bulk delete functionality works correctly', () => {
    render(<AssetList assets={mockAssets} loading={false} error={null} {...mockHandlers} />);
    
    // Initially, the Delete Selected button should not be visible
    expect(screen.queryByText(/delete selected/i)).not.toBeInTheDocument();
    
    // Select the first two assets
    const checkboxes = screen.getAllByRole('checkbox');
    fireEvent.click(checkboxes[1]); // First asset checkbox (index 0 is the select all checkbox)
    fireEvent.click(checkboxes[2]); // Second asset checkbox
    
    // Now the Delete Selected button should be visible
    const deleteSelectedButton = screen.getByText(/delete selected \(2\)/i);
    expect(deleteSelectedButton).toBeInTheDocument();
    
    // Click the Delete Selected button
    fireEvent.click(deleteSelectedButton);
    
    // Check if onBulkDeleteAssets was called with the correct asset IDs
    expect(mockHandlers.onBulkDeleteAssets).toHaveBeenCalledWith(['1', '2']);
  });

  test('select all checkbox works correctly', () => {
    render(<AssetList assets={mockAssets} loading={false} error={null} {...mockHandlers} />);
    
    // Get the select all checkbox (first checkbox in the table header)
    const selectAllCheckbox = screen.getAllByRole('checkbox')[0];
    
    // Click the select all checkbox
    fireEvent.click(selectAllCheckbox);
    
    // All Indian stock checkboxes should be checked (2 assets + select all = 3 checkboxes)
    const checkedBoxes = screen.getAllByRole('checkbox', { checked: true });
    expect(checkedBoxes.length).toBe(3);
    
    // Delete Selected button should show count of 2
    const deleteSelectedButton = screen.getByText(/delete selected \(2\)/i);
    expect(deleteSelectedButton).toBeInTheDocument();
    
    // Click the Delete Selected button
    fireEvent.click(deleteSelectedButton);
    
    // Check if onBulkDeleteAssets was called with the correct asset IDs
    expect(mockHandlers.onBulkDeleteAssets).toHaveBeenCalledWith(['1', '2']);
  });

  test('edit functionality works correctly', () => {
    render(<AssetList assets={mockAssets} loading={false} error={null} {...mockHandlers} />);
    
    // Find and click the edit button for the first asset
    const editButtons = screen.getAllByLabelText('edit asset');
    fireEvent.click(editButtons[0]);
    
    // Input fields should now be visible
    const priceInput = screen.getByRole('spinbutton', { name: /purchase_price/i });
    const quantityInput = screen.getByRole('spinbutton', { name: /quantity/i });
    const dateInput = screen.getByRole('textbox', { name: /purchase_date/i });
    
    // Change values
    fireEvent.change(priceInput, { target: { value: '2600' } });
    fireEvent.change(quantityInput, { target: { value: '12' } });
    fireEvent.change(dateInput, { target: { value: '2023-01-20' } });
    
    // Find and click the save button
    const saveButton = screen.getByLabelText('save asset');
    fireEvent.click(saveButton);
    
    // Check if onUpdateAsset was called with the correct parameters
    expect(mockHandlers.onUpdateAsset).toHaveBeenCalledWith('1', {
      symbol: 'RELIANCE.NS',
      asset_type: 'Indian Stock',
      purchase_price: 2600,
      quantity: 12,
      purchase_date: '2023-01-20'
    });
  });

  test('switching tabs clears selections', () => {
    render(<AssetList assets={mockAssets} loading={false} error={null} {...mockHandlers} />);
    
    // Select an asset in the Indian Stocks tab
    const checkboxes = screen.getAllByRole('checkbox');
    fireEvent.click(checkboxes[1]); // First asset checkbox
    
    // Delete Selected button should be visible
    expect(screen.getByText(/delete selected \(1\)/i)).toBeInTheDocument();
    
    // Switch to US Stocks tab
    fireEvent.click(screen.getByRole('tab', { name: /us stocks/i }));
    
    // Delete Selected button should no longer be visible
    expect(screen.queryByText(/delete selected/i)).not.toBeInTheDocument();
  });
});
