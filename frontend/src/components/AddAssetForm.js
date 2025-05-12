import React, { useState, useEffect } from 'react';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Box,
  Alert,
  Autocomplete // Added Autocomplete
} from '@mui/material';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import dayjs from 'dayjs';
import config from '../config';

// Constants for asset types - should ideally match backend
const ASSET_TYPE_INDIAN_STOCK = 'Indian Stock';
const ASSET_TYPE_US_STOCK = 'US Stock';
const ASSET_TYPE_CRYPTO = 'Crypto';

function AddAssetForm({ open, handleClose, onAssetAdded }) {
  const [symbol, setSymbol] = useState('');
  const [assetType, setAssetType] = useState(ASSET_TYPE_INDIAN_STOCK);
  const [purchasePrice, setPurchasePrice] = useState('');
  const [quantity, setQuantity] = useState('');
  const [purchaseDate, setPurchaseDate] = useState(dayjs()); // Default to today
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  // State for holding fetched symbol lists
  const [cryptoSymbols, setCryptoSymbols] = useState([]);
  const [indianStockSymbols, setIndianStockSymbols] = useState([]);
  const [usStockSymbols, setUsStockSymbols] = useState([]);
  const [symbolOptions, setSymbolOptions] = useState([]); // For Autocomplete

  // Effect to fetch all symbol lists on component mount
  useEffect(() => {
    const fetchSymbols = async (url, setter) => {
      try {
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`Failed to fetch symbols from ${url}`);
        }
        const data = await response.json();
        setter(data);
      } catch (err) {
        console.error(err);
        // Optionally set an error state here to inform the user
        setter([]); // Set to empty array on error
      }
    };

    fetchSymbols(config.api.endpoints.crypto, setCryptoSymbols);
    fetchSymbols(config.api.endpoints.indianStocks, setIndianStockSymbols);
    fetchSymbols(config.api.endpoints.usStocks, setUsStockSymbols);
  }, []); // Empty dependency array means this runs once on mount

  // Effect to update symbolOptions when assetType or fetched symbol lists change
  useEffect(() => {
    let currentOptions = [];
    if (assetType === ASSET_TYPE_CRYPTO) {
      currentOptions = cryptoSymbols;
    } else if (assetType === ASSET_TYPE_INDIAN_STOCK) {
      currentOptions = indianStockSymbols;
    } else if (assetType === ASSET_TYPE_US_STOCK) {
      currentOptions = usStockSymbols;
    }
    // The backend returns symbols as {id?, symbol, name}. 
    // Autocomplete needs options in a format like { label: 'BTC - Bitcoin', value: 'BTC' } or just strings.
    // We will format them to be objects with a label for display and value for submission.
    setSymbolOptions(
      currentOptions.map(s => ({
        label: `${s.symbol.toUpperCase()} - ${s.name}`,
        value: s.symbol.toUpperCase(),
        // Keep the original object in case we need other properties later
        // If Autocomplete's `isOptionEqualToValue` is not customized, it compares the option object itself.
        // So, it's often better to pass the full object and use getOptionLabel.
        ...s 
      }))
    );
    setSymbol(''); // Reset symbol when asset type changes
  }, [assetType, cryptoSymbols, indianStockSymbols, usStockSymbols]);

  const resetForm = () => {
    setSymbol('');
    setAssetType(ASSET_TYPE_INDIAN_STOCK);
    setPurchasePrice('');
    setQuantity('');
    setPurchaseDate(dayjs());
    setError(null);
  };

  const handleSubmit = async () => {
    if (!symbol || !assetType || !purchasePrice || !quantity || !purchaseDate) {
      setError('All fields are required.');
      return;
    }
    if (isNaN(parseFloat(purchasePrice)) || parseFloat(purchasePrice) <= 0) {
        setError('Purchase price must be a positive number.');
        return;
    }
    if (isNaN(parseFloat(quantity)) || parseFloat(quantity) <= 0) {
        setError('Quantity must be a positive number.');
        return;
    }

    const newAsset = {
      symbol: symbol.toUpperCase(),
      asset_type: assetType,
      purchase_price: parseFloat(purchasePrice),
      quantity: parseFloat(quantity),
      purchase_date: purchaseDate.format('YYYY-MM-DD'),
    };

    setSubmitting(true);
    setError(null);

    try {
      const response = await fetch(config.api.endpoints.assets, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newAsset),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Failed to add asset' }));
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }
      
      // const addedAsset = await response.json(); // Contains the ID from backend
      await response.json(); // Consume the response body

      onAssetAdded(); // Callback to refresh asset list
      resetForm();
      handleClose(); // Close the dialog
    } catch (e) {
      console.error("Failed to add asset:", e);
      setError(e.message || "An unexpected error occurred.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDialogClose = () => {
    if (submitting) return; // Don't close if submitting
    resetForm();
    handleClose();
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Dialog open={open} onClose={handleDialogClose} fullWidth maxWidth="sm">
        <DialogTitle>Add New Asset</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            Enter the details of the new asset you want to add to your portfolio.
          </DialogContentText>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          <Box component="form" noValidate autoComplete="off">
            <FormControl fullWidth margin="dense" sx={{ mb: 2 }} disabled={submitting}>
              <InputLabel id="asset-type-label">Asset Type</InputLabel>
              <Select
                autoFocus // Moved autoFocus here
                labelId="asset-type-label"
                id="assetType"
                value={assetType}
                label="Asset Type"
                onChange={(e) => setAssetType(e.target.value)}
              >
                <MenuItem value={ASSET_TYPE_INDIAN_STOCK}>{ASSET_TYPE_INDIAN_STOCK}</MenuItem>
                <MenuItem value={ASSET_TYPE_US_STOCK}>{ASSET_TYPE_US_STOCK}</MenuItem>
                <MenuItem value={ASSET_TYPE_CRYPTO}>{ASSET_TYPE_CRYPTO}</MenuItem>
              </Select>
            </FormControl>
            <Autocomplete
              freeSolo // Allows free text input
              id="symbol-autocomplete"
              options={symbolOptions}
              getOptionLabel={(option) => option.label || ''} // Handles case where option might be a string or object
              value={symbolOptions.find(opt => opt.value === symbol) || null} // Controlled component: find the object that matches current symbol string
              onChange={(event, newValue) => {
                if (typeof newValue === 'string') {
                  setSymbol(newValue.toUpperCase()); // User typed a new string
                } else if (newValue && newValue.value) {
                  setSymbol(newValue.value); // User selected an option from the list
                } else {
                  setSymbol(''); // Cleared
                }
              }}
              onInputChange={(event, newInputValue) => {
                // If freeSolo, and user types, we might want to setSymbol directly here too,
                // depending on desired UX. For now, onChange handles selection or custom string entry.
                // This is more for when the input text itself changes without selecting an option.
                // For this setup, relying on onChange is usually sufficient.
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Stock Symbol / Crypto Ticker"
                  variant="outlined"
                  margin="dense"
                  error={!!error && symbol === ''} // Example: show error if symbol is empty and form submitted
                  helperText={error && symbol === '' ? 'Symbol is required' : ''}
                />
              )}
              sx={{ mb: 2 }}
              disabled={submitting}
            />
            <TextField
              margin="dense"
              id="purchasePrice"
              label="Purchase Price (per unit)"
              type="number"
              fullWidth
              variant="outlined"
              value={purchasePrice}
              onChange={(e) => setPurchasePrice(e.target.value)}
              disabled={submitting}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              id="quantity"
              label="Quantity"
              type="number"
              fullWidth
              variant="outlined"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              disabled={submitting}
              sx={{ mb: 2 }}
            />
            <DatePicker
              label="Purchase Date"
              value={purchaseDate}
              onChange={(newValue) => setPurchaseDate(newValue)}
              disabled={submitting}
              sx={{ width: '100%', mb: 2 }}
              textField={(params) => <TextField {...params} fullWidth margin="dense" />}
            />
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: '16px 24px'}}>
          <Button onClick={handleDialogClose} disabled={submitting} color="secondary">Cancel</Button>
          <Button onClick={handleSubmit} disabled={submitting} variant="contained">
            {submitting ? 'Adding...' : 'Add Asset'}
          </Button>
        </DialogActions>
      </Dialog>
    </LocalizationProvider>
  );
}

export default AddAssetForm;
