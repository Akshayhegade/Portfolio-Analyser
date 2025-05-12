import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Chip,
  CircularProgress,
  IconButton,
  Tooltip,
  Paper
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import HorizontalRuleIcon from '@mui/icons-material/HorizontalRule';
import config from '../config';

/**
 * Component for displaying live price information for an asset
 */
const LivePriceInfo = ({ asset }) => {
  const [livePrice, setLivePrice] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Calculate profit/loss
  const calculateProfitLoss = () => {
    if (!livePrice || !asset) return null;

    const currentValue = livePrice * asset.quantity;
    const costBasis = asset.purchase_price * asset.quantity;
    const profitLoss = currentValue - costBasis;
    const profitLossPercent = (profitLoss / costBasis) * 100;

    return {
      value: profitLoss,
      percent: profitLossPercent,
      currentValue
    };
  };

  // Fetch the price for this specific asset
  const fetchPrice = async () => {
    if (!asset || !asset.symbol) return;

    setLoading(true);
    setError(null);

    try {
      const url = config.api.endpoints.priceForSymbol(asset.symbol);
      const params = new URLSearchParams({ type: asset.asset_type });
      
      const response = await fetch(`${url}?${params}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch price: ${response.statusText}`);
      }
      
      const data = await response.json();
      setLivePrice(data.price);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Error fetching price:', err);
      setError(err.message || 'Failed to fetch price data');
    } finally {
      setLoading(false);
    }
  };

  // Fetch price on mount and when asset changes
  useEffect(() => {
    fetchPrice();
    
    // Refresh every 5 minutes (300000 ms)
    const interval = setInterval(fetchPrice, 300000);
    
    return () => clearInterval(interval);
  }, [asset?.id, asset?.symbol]);

  // Calculate profit/loss
  const profitLoss = calculateProfitLoss();

  // Format values for display
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2
    }).format(value);
  };

  // Render profit/loss indicator
  const renderProfitLossIndicator = () => {
    if (!profitLoss) return null;
    
    const { value, percent } = profitLoss;
    
    if (value > 0) {
      return (
        <Chip
          icon={<TrendingUpIcon />}
          label={`+${percent.toFixed(2)}%`}
          color="success"
          size="small"
          variant="outlined"
        />
      );
    } else if (value < 0) {
      return (
        <Chip
          icon={<TrendingDownIcon />}
          label={`${percent.toFixed(2)}%`}
          color="error"
          size="small"
          variant="outlined"
        />
      );
    } else {
      return (
        <Chip
          icon={<HorizontalRuleIcon />}
          label="0.00%"
          color="default"
          size="small"
          variant="outlined"
        />
      );
    }
  };

  if (loading) {
    return (
      <Box display="flex" alignItems="center">
        <CircularProgress size={16} />
        <Typography variant="body2" sx={{ ml: 1 }}>Loading price...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Tooltip title={error}>
        <Typography variant="body2" color="error">
          Price unavailable
          <IconButton size="small" onClick={fetchPrice}>
            <RefreshIcon fontSize="small" />
          </IconButton>
        </Typography>
      </Tooltip>
    );
  }

  if (!livePrice) {
    return (
      <Box display="flex" alignItems="center">
        <Typography variant="body2" color="text.secondary">
          No price data
          <IconButton size="small" onClick={fetchPrice}>
            <RefreshIcon fontSize="small" />
          </IconButton>
        </Typography>
      </Box>
    );
  }

  return (
    <Paper variant="outlined" sx={{ p: 1, mb: 1 }}>
      <Box display="flex" flexDirection="column">
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="body2" fontWeight="bold">
            Current Price:
          </Typography>
          <Typography variant="body1">
            {formatCurrency(livePrice)}
          </Typography>
        </Box>
        
        {profitLoss && (
          <>
            <Box display="flex" justifyContent="space-between" alignItems="center" mt={0.5}>
              <Typography variant="body2">
                P/L:
              </Typography>
              <Box display="flex" alignItems="center">
                <Typography 
                  variant="body2" 
                  color={profitLoss.value >= 0 ? 'success.main' : 'error.main'}
                  mr={1}
                >
                  {formatCurrency(profitLoss.value)}
                </Typography>
                {renderProfitLossIndicator()}
              </Box>
            </Box>
            
            <Box display="flex" justifyContent="space-between" alignItems="center" mt={0.5}>
              <Typography variant="body2">
                Current Value:
              </Typography>
              <Typography variant="body2">
                {formatCurrency(profitLoss.currentValue)}
              </Typography>
            </Box>
          </>
        )}
        
        <Box display="flex" justifyContent="flex-end" alignItems="center" mt={0.5}>
          <Typography variant="caption" color="text.secondary">
            {lastUpdated ? `Updated: ${lastUpdated.toLocaleTimeString()}` : ''}
          </Typography>
          <IconButton size="small" onClick={fetchPrice} sx={{ ml: 0.5 }}>
            <RefreshIcon fontSize="small" />
          </IconButton>
        </Box>
      </Box>
    </Paper>
  );
};

export default LivePriceInfo;
