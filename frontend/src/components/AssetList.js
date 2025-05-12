import React, { useState, useEffect } from 'react';
import Checkbox from '@mui/material/Checkbox'; // Added Checkbox
import Button from '@mui/material/Button'; // Added Button
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Box,
  Tabs,
  Tab,
  IconButton,
  TextField, // Added TextField
  Switch,
  FormControlLabel
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import SaveIcon from '@mui/icons-material/Save'; // Added SaveIcon
import LivePriceInfo from './LivePriceInfo'; // Import LivePriceInfo component

// Constants for asset types (can be received as props or defined locally if sure they won't change)
const ASSET_TYPE_INDIAN_STOCK = 'Indian Stock';
const ASSET_TYPE_US_STOCK = 'US Stock';
const ASSET_TYPE_CRYPTO = 'Crypto';

// Helper function for TabPanel a11y props
function a11yProps(index) {
  return {
    id: `asset-class-tab-${index}`,
    'aria-controls': `asset-class-tabpanel-${index}`,
  };
}

// TabPanel component (remains the same)
function TabPanel(props) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`asset-class-tabpanel-${index}`}
      aria-labelledby={`asset-class-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ pt: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

// AssetList now receives assets, loading, and error as props
function AssetList({ assets, loading, error, onDeleteAsset, onUpdateAsset, onBulkDeleteAssets }) { // Added onBulkDeleteAssets prop 
  const [selectedTabValue, setSelectedTabValue] = useState(0);
  const [editingAssetId, setEditingAssetId] = useState(null);
  const [editedAssetData, setEditedAssetData] = useState({});
  const [showLivePrices, setShowLivePrices] = useState(true); // State to toggle live price display
  const [selectedAssets, setSelectedAssets] = useState([]); // State for selected asset IDs

  const handleEditDataChange = (event) => {
    const { name, value, type } = event.target;
    // For number inputs, parse to float or default to 0 if parsing fails (e.g. empty string)
    // For date and other inputs, use the value directly.
    const processedValue = type === 'number' ? (value === '' ? '' : parseFloat(value)) : value;
    
    setEditedAssetData(prevData => ({
      ...prevData,
      // Ensure that if a number field is cleared, it becomes an empty string or a specific placeholder
      // rather than NaN, which can cause issues. Or handle validation on save.
      [name]: processedValue
    }));
  };

  // Effect to reset tab if assets change drastically (e.g., all assets of current tab type are removed)
  // This is optional and depends on desired UX.
  useEffect(() => {
    const currentTabAssets = () => {
        if (selectedTabValue === 0) return assets.filter(asset => asset.asset_type === ASSET_TYPE_INDIAN_STOCK);
        if (selectedTabValue === 1) return assets.filter(asset => asset.asset_type === ASSET_TYPE_US_STOCK);
        if (selectedTabValue === 2) return assets.filter(asset => asset.asset_type === ASSET_TYPE_CRYPTO);
        return [];
    };
    if (currentTabAssets().length === 0 && assets.length > 0) {
        // If current tab becomes empty but other assets exist, try to find a non-empty tab
        if (assets.filter(asset => asset.asset_type === ASSET_TYPE_INDIAN_STOCK).length > 0) setSelectedTabValue(0);
        else if (assets.filter(asset => asset.asset_type === ASSET_TYPE_US_STOCK).length > 0) setSelectedTabValue(1);
        else if (assets.filter(asset => asset.asset_type === ASSET_TYPE_CRYPTO).length > 0) setSelectedTabValue(2);
        // else all are empty, no change needed, main component will show "No assets"
    }
  }, [assets, selectedTabValue]);

  const handleTabChange = (event, newValue) => {
    setSelectedTabValue(newValue);
    setSelectedAssets([]); // Clear selections when changing tabs
  };

  const handleSelectAllClick = (event, assetsOfType) => {
    if (event.target.checked) {
      const newSelecteds = assetsOfType.map((n) => n.id);
      setSelectedAssets(newSelecteds);
      return;
    }
    setSelectedAssets([]);
  };

  const handleCheckboxClick = (event, id) => {
    const selectedIndex = selectedAssets.indexOf(id);
    let newSelected = [];

    if (selectedIndex === -1) {
      newSelected = newSelected.concat(selectedAssets, id);
    } else if (selectedIndex === 0) {
      newSelected = newSelected.concat(selectedAssets.slice(1));
    } else if (selectedIndex === selectedAssets.length - 1) {
      newSelected = newSelected.concat(selectedAssets.slice(0, -1));
    } else if (selectedIndex > 0) {
      newSelected = newSelected.concat(
        selectedAssets.slice(0, selectedIndex),
        selectedAssets.slice(selectedIndex + 1),
      );
    }
    setSelectedAssets(newSelected);
  };

  const handleBulkDelete = () => {
    if (onBulkDeleteAssets) {
      onBulkDeleteAssets(selectedAssets);
      setSelectedAssets([]); // Clear selection after deletion
    }
  };

  // Loading and error are now handled by the parent (App.js) primarily.
  // AssetList can show its own loading spinner for tab content if desired,
  // but main loading/error for asset fetch is handled by App.js.
  if (loading) {
    return <CircularProgress />;
  }

  // Error passed from App.js (though App.js already displays a primary error alert)
  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  const indianStocks = assets.filter(asset => asset.asset_type === ASSET_TYPE_INDIAN_STOCK);
  const usStocks = assets.filter(asset => asset.asset_type === ASSET_TYPE_US_STOCK);
  const cryptoAssets = assets.filter(asset => asset.asset_type === ASSET_TYPE_CRYPTO);

  const renderAssetTable = (assetsOfType, assetTypeNameForEmptyMessage) => {
    const numSelected = selectedAssets.filter(id => assetsOfType.some(asset => asset.id === id)).length;
    const rowCount = assetsOfType.length;

    if (assetsOfType.length === 0) {
      return <Typography variant="subtitle1">No {assetTypeNameForEmptyMessage.toLowerCase()} added yet.</Typography>;
    }
    return (
      <Box>
        {numSelected > 0 && (
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1, mr:1 }}>
            <Button variant="contained" color="secondary" onClick={handleBulkDelete}>
              Delete Selected ({numSelected})
            </Button>
          </Box>
        )}
        <TableContainer component={Paper} variant="outlined">
        <Table sx={{ minWidth: 650 }} aria-label={`${assetTypeNameForEmptyMessage} table`}>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  indeterminate={numSelected > 0 && numSelected < rowCount}
                  checked={rowCount > 0 && numSelected === rowCount}
                  onChange={(event) => handleSelectAllClick(event, assetsOfType)}
                  inputProps={{ 'aria-label': 'select all assets' }}
                />
              </TableCell>
              <TableCell>Symbol</TableCell>
              <TableCell align="right">Purchase Price (INR)</TableCell>
              <TableCell align="right">Quantity</TableCell>
              <TableCell>Purchase Date</TableCell>
              {showLivePrices && <TableCell>Live Price Info</TableCell>}
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {assetsOfType.map((asset) => (
              <TableRow
                key={asset.id}
                selected={selectedAssets.indexOf(asset.id) !== -1}
                sx={{ '&:last-child td, &:last-child th': { border: 0 }, cursor: 'pointer' }}
                hover
                onClick={(event) => {
                  // Prevent row click from triggering when clicking on interactive elements like buttons/textfields
                  if (event.target.closest('button, input, a')) {
                    return;
                  }
                  handleCheckboxClick(event, asset.id)
                }}
                role="checkbox"
                aria-checked={selectedAssets.indexOf(asset.id) !== -1}
                tabIndex={-1}
              >
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={selectedAssets.indexOf(asset.id) !== -1}
                    onChange={(event) => handleCheckboxClick(event, asset.id)} // Ensure direct click on checkbox also works
                    inputProps={{ 'aria-labelledby': `asset-checkbox-${asset.id}` }}
                  />
                </TableCell>
                <TableCell component="th" scope="row">
                  <Box fontWeight="bold">{asset.symbol}</Box>
                </TableCell>
                {editingAssetId === asset.id ? (
                  <>
                    <TableCell align="right">
                      <TextField
                        type="number"
                        name="purchase_price"
                        value={editedAssetData.purchase_price || ''}
                        onChange={handleEditDataChange}
                        size="small"
                        variant="outlined"
                        sx={{ width: '120px' }} // Adjust width as needed
                      />
                    </TableCell>
                    <TableCell align="right">
                      <TextField
                        type="number"
                        name="quantity"
                        value={editedAssetData.quantity || ''}
                        onChange={handleEditDataChange}
                        size="small"
                        variant="outlined"
                        sx={{ width: '80px' }} // Adjust width as needed
                      />
                    </TableCell>
                    <TableCell>
                      <TextField
                        type="date"
                        name="purchase_date"
                        value={editedAssetData.purchase_date || ''}
                        onChange={handleEditDataChange}
                        size="small"
                        variant="outlined"
                        InputLabelProps={{ shrink: true }}
                        sx={{ width: '150px' }} // Adjust width as needed
                      />
                    </TableCell>
                  </>
                ) : (
                  <>
                    <TableCell align="right">{asset.purchase_price.toFixed(2)}</TableCell>
                    <TableCell align="right">{asset.quantity}</TableCell>
                    <TableCell>{asset.purchase_date}</TableCell>
                    {showLivePrices && (
                      <TableCell>
                        <LivePriceInfo asset={asset} />
                      </TableCell>
                    )}
                  </>
                )}
                <TableCell>
                  {editingAssetId === asset.id ? (
                    <IconButton
                      aria-label="save asset"
                      size="small"
                      onClick={async () => {
                        // Basic validation: Ensure required fields are not empty
                        if (!editedAssetData.purchase_price || !editedAssetData.quantity || !editedAssetData.purchase_date) {
                          console.error("Validation Error: Price, Quantity, and Date cannot be empty.");
                          // Optionally, provide user feedback here (e.g., using a snackbar or alert)
                          return; // Prevent API call if validation fails
                        }
                        const success = await onUpdateAsset(editingAssetId, editedAssetData);
                        if (success) {
                          setEditingAssetId(null);
                          setEditedAssetData({});
                        }
                      }}
                      sx={{ mr: 0.5 }}
                      color="primary"
                    >
                      <SaveIcon fontSize="small" />
                    </IconButton>
                  ) : (
                    <IconButton
                      aria-label="edit asset"
                      size="small"
                      onClick={() => {
                        setEditingAssetId(asset.id);
                        setEditedAssetData({ ...asset }); // Initialize form with current asset data
                      }}
                      sx={{ mr: 0.5 }}
                    >
                      <EditIcon fontSize="small" />
                    </IconButton>
                  )}
                  <IconButton
                    aria-label="delete asset"
                    size="small"
                    color="error"
                    onClick={() => onDeleteAsset(asset.id)}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      </Box>
    );
  };

  // App.js will show a general "No assets added yet" if total assets are zero.
  // This check is more for internal consistency or if AssetList were used standalone.
  if (assets.length === 0 && !loading) {
    // This message might be redundant if App.js handles the global empty state.
    // Consider removing or adjusting based on App.js behavior.
    return (
      <div>
        <Typography variant="h6">No assets in your portfolio. Add some to get started!</Typography>
      </div>
    );
  }

  return (
    <div>
      {/* Toggle switch for live prices */}
      <Box display="flex" justifyContent="flex-end" mb={2}>
        <FormControlLabel
          control={
            <Switch
              checked={showLivePrices}
              onChange={(e) => setShowLivePrices(e.target.checked)}
              color="primary"
            />
          }
          label="Show Live Prices"
        />
      </Box>
      
      <Box sx={{ width: '100%' }}>
        <Tabs value={selectedTabValue} onChange={handleTabChange} aria-label="asset tabs" sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab label="Indian Stocks" {...a11yProps(0)} />
          <Tab label="US Stocks" {...a11yProps(1)} />
          <Tab label="Crypto" {...a11yProps(2)} />
        </Tabs>
        <TabPanel value={selectedTabValue} index={0}>
          {renderAssetTable(indianStocks, 'Indian Stocks')}
        </TabPanel>
        <TabPanel value={selectedTabValue} index={1}>
          {renderAssetTable(usStocks, 'US Stocks')}
        </TabPanel>
        <TabPanel value={selectedTabValue} index={2}>
          {renderAssetTable(cryptoAssets, 'Cryptocurrencies')}
        </TabPanel>
      </Box>
    </div>
  );
}

export default AssetList;
