import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Fab,
  Grid,
  Paper,
  CircularProgress,
  Alert,
  IconButton,
  Divider,
  Button,
  useTheme,
  useMediaQuery
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import RefreshIcon from '@mui/icons-material/Refresh';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import AssetList from './components/AssetList';
import AddAssetForm from './components/AddAssetForm';
import PortfolioCharts from './components/PortfolioCharts';
import config from './config';

const ASSET_TYPE_INDIAN_STOCK = 'Indian Stock';
const ASSET_TYPE_US_STOCK = 'US Stock';
const ASSET_TYPE_CRYPTO = 'Crypto';

// Helper function to format numbers in Indian currency style (K, L, Cr)
const formatIndianCurrency = (num) => {
  if (num === null || num === undefined) return '0';
  const n = parseFloat(num);
  if (isNaN(n)) return '0';

  if (Math.abs(n) >= 10000000) { // Crore
    return (n / 10000000).toFixed(2) + ' Cr';
  } else if (Math.abs(n) >= 100000) { // Lakh
    return (n / 100000).toFixed(2) + ' L';
  } else if (Math.abs(n) >= 1000) { // Thousand
    return (n / 1000).toFixed(2) + ' K';
  }
  return n.toFixed(2);
};

const summaryBoxStyles = {
  indianStocks: {
    background: 'linear-gradient(45deg, rgba(63, 81, 181, 0.05) 0%, rgba(63, 81, 181, 0.1) 100%)',
    borderLeft: '4px solid #3f51b5',
    minHeight: '120px',
    display: 'flex', 
    flexDirection: 'column',
    justifyContent: 'center',
    height: '100%' // Ensure Paper fills Grid item height
  },
  usStocks: {
    background: 'linear-gradient(45deg, rgba(94, 53, 177, 0.05) 0%, rgba(94, 53, 177, 0.1) 100%)',
    borderLeft: '4px solid #5e35b1',
    color: 'text.primary',
    minHeight: '120px',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    height: '100%'
  },
  crypto: {
    background: 'linear-gradient(45deg, rgba(46, 125, 50, 0.05) 0%, rgba(46, 125, 50, 0.1) 100%)',
    borderLeft: '4px solid #2e7d32',
    color: 'text.primary',
    minHeight: '120px',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    height: '100%'
  },
  total: {
    background: 'linear-gradient(45deg, rgba(0, 0, 0, 0.05) 0%, rgba(121, 85, 72, 0.1) 100%)',
    borderLeft: '4px solid #795548',
    color: 'text.primary',
    minHeight: '120px',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    height: '100%'
  }
};

function App() {
  const [addAssetModalOpen, setAddAssetModalOpen] = useState(false);
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [livePrices, setLivePrices] = useState({});
  const [loadingPrices, setLoadingPrices] = useState(false);
  const [priceError, setPriceError] = useState(null);
  const [lastPriceUpdate, setLastPriceUpdate] = useState(null);

  // Purchase value totals (based on what user paid)
  const [indianStocksTotal, setIndianStocksTotal] = useState(0);
  const [usStocksTotal, setUsStocksTotal] = useState(0);
  const [cryptoTotal, setCryptoTotal] = useState(0);
  const [grandTotal, setGrandTotal] = useState(0);
  
  // Current value totals (based on live prices)
  const [indianStocksCurrentTotal, setIndianStocksCurrentTotal] = useState(0);
  const [usStocksCurrentTotal, setUsStocksCurrentTotal] = useState(0);
  const [cryptoCurrentTotal, setCryptoCurrentTotal] = useState(0);
  const [grandCurrentTotal, setGrandCurrentTotal] = useState(0);

  const fetchAssets = async () => {
    setLoading(true);
    try {
      const response = await fetch(config.api.endpoints.assets);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setAssets(data);
      setError(null);
      
      // Fetch live prices for these assets
      fetchLivePrices(data);
    } catch (e) {
      console.error("Failed to fetch assets:", e);
      setError("Failed to load assets. Backend might be down or CORS issue.");
      setAssets([]);
    } finally {
      setLoading(false);
    }
  };
  
  // Fetch live prices for all assets
  const fetchLivePrices = async (assetsList = assets) => {
    if (!assetsList.length) return;
    
    setLoadingPrices(true);
    setPriceError(null);
    
    try {
      const response = await fetch(config.api.endpoints.prices, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ assets: assetsList }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const priceData = await response.json();
      setLivePrices(priceData);
      setLastPriceUpdate(new Date());
    } catch (e) {
      console.error("Failed to fetch live prices:", e);
      setPriceError("Failed to load live prices. Some features may be limited.");
    } finally {
      setLoadingPrices(false);
    }
  };
  
  // Refresh live prices manually
  const handleRefreshPrices = () => {
    fetchLivePrices();
  };

  useEffect(() => { 
    fetchAssets(); 
    
    // Set up an interval to refresh prices every 5 minutes
    const intervalId = setInterval(() => {
      fetchLivePrices();
    }, 5 * 60 * 1000);
    
    return () => clearInterval(intervalId);
  }, []);

  useEffect(() => {
    // Calculate purchase value totals
    let indTotal = 0, usTotal = 0, cryTotal = 0;
    // Calculate current value totals if we have prices
    let indCurrentTotal = 0, usCurrentTotal = 0, cryCurrentTotal = 0;
    
    assets.forEach(asset => {
      // Purchase value (what user paid)
      const purchaseValue = asset.purchase_price * asset.quantity;
      
      // Current value (based on live price if available)
      const livePrice = livePrices[asset.symbol];
      const currentValue = livePrice ? livePrice * asset.quantity : purchaseValue;
      
      // Add to appropriate totals based on asset type
      if (asset.asset_type === ASSET_TYPE_INDIAN_STOCK) {
        indTotal += purchaseValue;
        indCurrentTotal += currentValue;
      }
      else if (asset.asset_type === ASSET_TYPE_US_STOCK) {
        usTotal += purchaseValue;
        usCurrentTotal += currentValue;
      }
      else if (asset.asset_type === ASSET_TYPE_CRYPTO) {
        cryTotal += purchaseValue;
        cryCurrentTotal += currentValue;
      }
    });
    
    // Update purchase value states
    setIndianStocksTotal(indTotal);
    setUsStocksTotal(usTotal);
    setCryptoTotal(cryTotal);
    setGrandTotal(indTotal + usTotal + cryTotal);
    
    // Update current value states
    setIndianStocksCurrentTotal(indCurrentTotal);
    setUsStocksCurrentTotal(usCurrentTotal);
    setCryptoCurrentTotal(cryCurrentTotal);
    setGrandCurrentTotal(indCurrentTotal + usCurrentTotal + cryCurrentTotal);
  }, [assets, livePrices]);

  const handleOpenAddAssetModal = () => setAddAssetModalOpen(true);
  const handleCloseAddAssetModal = () => setAddAssetModalOpen(false);
  const handleAssetAdded = () => fetchAssets();

  const handleDeleteAsset = async (assetId) => {
    // Optimistically update UI or show loading state if preferred
    // For now, directly attempt deletion and update on success
    try {
      const response = await fetch(`${config.api.endpoints.assets}/${assetId}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        // Attempt to read error message from backend if available
        const errorData = await response.json().catch(() => null); // Catch if body is not json or empty
        throw new Error(errorData?.message || `HTTP error! status: ${response.status}`);
      }
      // On successful deletion, filter out the asset from the local state
      setAssets(currentAssets => currentAssets.filter(asset => asset.id !== assetId));
      setError(null); // Clear any previous errors
      // Optionally, show a success message to the user
    } catch (e) {
      console.error("Failed to delete asset:", e);
      setError(`Failed to delete asset: ${e.message}`);
      // Potentially re-fetch assets to ensure UI consistency if optimistic update failed badly
      // fetchAssets(); 
    }
  };

  const handleBulkDeleteAssets = async (assetIds) => {
    if (!assetIds || assetIds.length === 0) {
      return; // No assets selected to delete
    }
    console.log("Attempting to delete asset IDs:", assetIds);
    try {
      // Make sure the URL doesn't have a trailing slash
      const url = config.api.endpoints.assets.endsWith('/') 
        ? config.api.endpoints.assets.slice(0, -1) 
        : config.api.endpoints.assets;
      
      const response = await fetch(url, { 
        method: 'DELETE',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ ids: assetIds }), // Sending IDs in the body
        credentials: 'omit' // Don't send cookies with the request
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: `HTTP error! status: ${response.status}` }));
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('Bulk delete successful', result);
      
      fetchAssets(); // Re-fetch all assets to update the list and summaries
      setError(null);
    } catch (e) {
      console.error("Failed to bulk delete assets:", e);
      setError(`Failed to delete selected assets: ${e.message}. Please try again.`);
    }
  };

  const handleUpdateAsset = async (assetId, updatedData) => {
    try {
      const response = await fetch(`${config.api.endpoints.assets}/${assetId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedData),
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.message || `HTTP error! status: ${response.status}`);
      }
      const returnedAsset = await response.json(); // Get the updated asset from the response
      setAssets(currentAssets => 
        currentAssets.map(asset => 
          asset.id === assetId ? returnedAsset : asset
        )
      );
      setError(null);
      return true; // Indicate success
    } catch (e) {
      console.error("Failed to update asset:", e);
      setError(`Failed to update asset: ${e.message}`);
      return false; // Indicate failure
    }
  };
  
  const renderSummaryBox = (title, purchaseValue, currentValue, styleProps, gridProps) => {
    const isProfitable = currentValue > purchaseValue;
    const isNeutral = currentValue === purchaseValue;
    const percentChange = purchaseValue > 0 ? ((currentValue - purchaseValue) / purchaseValue) * 100 : 0;
    
    return (
      <Grid item {...gridProps}>
        <Paper elevation={3} sx={{ p: 2, ...styleProps }}>
          <Typography variant="subtitle1" component="h2" sx={{ fontWeight: 'bold', textAlign: 'center' }}>
            {title}
          </Typography>
          
          {/* Purchase Value */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
            <Typography variant="body2">Purchase Value:</Typography>
            <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
              {loading ? <CircularProgress size={16} color="inherit" /> : `₹${formatIndianCurrency(purchaseValue)}`}
            </Typography>
          </Box>
          
          {/* Current Value */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
            <Typography variant="body2">Current Value:</Typography>
            <Typography 
              variant="body1" 
              sx={{ 
                fontWeight: 'bold',
                color: loadingPrices ? 'text.primary' : (isProfitable ? 'success.main' : (isNeutral ? 'text.primary' : 'error.main'))
              }}
            >
              {loadingPrices ? <CircularProgress size={16} color="inherit" /> : `₹${formatIndianCurrency(currentValue)}`}
            </Typography>
          </Box>
          
          {/* Profit/Loss Percentage */}
          {!loading && !loadingPrices && purchaseValue > 0 && (
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
              <Typography 
                variant="body2" 
                sx={{ 
                  fontWeight: 'bold',
                  color: isProfitable ? 'success.main' : (isNeutral ? 'text.primary' : 'error.main')
                }}
              >
                {isProfitable ? '+' : ''}{percentChange.toFixed(2)}%
              </Typography>
            </Box>
          )}
        </Paper>
      </Grid>
    );
  };

  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static" elevation={1}>
        <Toolbar>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <AnalyticsIcon sx={{ mr: 1.5 }} />
            <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
              Portfolio Analyser
            </Typography>
          </Box>
          <Box sx={{ flexGrow: 1 }} />
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {lastPriceUpdate && (
              <Typography 
                variant="body2" 
                sx={{ 
                  mr: 2, 
                  display: { xs: 'none', sm: 'block' },
                  fontWeight: 500,
                  color: theme.palette.primary.light,
                  bgcolor: 'rgba(255,255,255,0.15)',
                  px: 1.5,
                  py: 0.5,
                  borderRadius: 1
                }}
              >
                Last update: {lastPriceUpdate.toLocaleTimeString()}
              </Typography>
            )}
            <Button 
              color="inherit" 
              startIcon={<RefreshIcon />} 
              onClick={handleRefreshPrices}
              disabled={loadingPrices}
              sx={{ display: { xs: 'none', sm: 'flex' } }}
            >
              {loadingPrices ? 'Updating...' : 'Refresh Prices'}
            </Button>
          </Box>
        </Toolbar>
      </AppBar>
      <Container component="main" sx={{ my: 4, flexGrow: 1 }}>
        <Box sx={{ mb: 4, display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleOpenAddAssetModal}
            sx={{ display: { xs: 'none', sm: 'flex' } }}
          >
            Add Asset
          </Button>
        </Box>

        {/* Error message container */}
        {priceError && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="error">
              {priceError}
            </Typography>
          </Box>
        )}

        {/* Portfolio Charts */}
        <Box sx={{ width: '100%' }}>
          <PortfolioCharts 
            assets={assets}
            indianStocksTotal={indianStocksTotal}
            usStocksTotal={usStocksTotal}
            cryptoTotal={cryptoTotal}
            indianStocksCurrentTotal={indianStocksCurrentTotal}
            usStocksCurrentTotal={usStocksCurrentTotal}
            cryptoCurrentTotal={cryptoCurrentTotal}
            loading={loading}
            loadingPrices={loadingPrices}
          />
        </Box>
        
        <Divider sx={{ my: 4 }} />
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" component="h2" sx={{ fontWeight: 600 }}>
            Asset Management
          </Typography>
          {isSmallScreen && (
            <Button
              variant="outlined"
              size="small"
              startIcon={<AddIcon />}
              onClick={handleOpenAddAssetModal}
            >
              Add
            </Button>
          )}
        </Box>
        
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <Paper elevation={2} sx={{ 
          p: 2, 
          borderRadius: 2, 
          overflow: 'hidden',
          border: `1px solid ${theme.palette.divider}`,
          transition: 'all 0.3s ease-in-out'
        }}>
          <AssetList 
            assets={assets} 
            loading={loading}
            error={error} 
            onDeleteAsset={handleDeleteAsset}
            onUpdateAsset={handleUpdateAsset}
            onBulkDeleteAssets={handleBulkDeleteAssets} // Pass the new handler
          />
        </Paper>
      </Container>

      <AddAssetForm open={addAssetModalOpen} handleClose={handleCloseAddAssetModal} onAssetAdded={handleAssetAdded} />
      <Fab 
        color="primary" 
        aria-label="add asset" 
        sx={{ 
          position: 'fixed', 
          bottom: 24, 
          right: 24,
          boxShadow: 6,
          '&:hover': {
            transform: 'scale(1.1)',
            boxShadow: 8
          }
        }} 
        onClick={handleOpenAddAssetModal}
      >
        <AddIcon />
      </Fab>

      <Box 
        component="footer" 
        sx={{ 
          py: 3, 
          px: 2, 
          mt: 'auto', 
          borderTop: `1px solid ${theme.palette.divider}`,
          backgroundColor: theme.palette.background.paper
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={2} justifyContent="space-between" alignItems="center">
            <Grid item>
              <Typography variant="body2" color="text.secondary">
                © {new Date().getFullYear()} Portfolio Analyser
              </Typography>
            </Grid>
            <Grid item>
              <Typography variant="body2" color="text.secondary">
                {lastPriceUpdate && `Last price update: ${lastPriceUpdate.toLocaleTimeString()}`}
              </Typography>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </Box>
  );
}

export default App;
