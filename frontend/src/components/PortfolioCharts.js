import React from 'react';
import { Box, Paper, Typography, Grid, useTheme, CircularProgress } from '@mui/material';

/**
 * Component for displaying portfolio data in various chart formats
 */
const PortfolioCharts = ({ 
  assets = [], 
  indianStocksTotal = 0, 
  usStocksTotal = 0, 
  cryptoTotal = 0,
  indianStocksCurrentTotal = 0,
  usStocksCurrentTotal = 0,
  cryptoCurrentTotal = 0,
  loading = false,
  loadingPrices = false
}) => {
  const theme = useTheme();
  
  // Calculate values based on the assets
  
  // Calculate total values
  const totalPortfolioValue = (
    (indianStocksCurrentTotal || 0) + 
    (usStocksCurrentTotal || 0) + 
    (cryptoCurrentTotal || 0)
  );
  
  const totalPurchaseValue = (
    (indianStocksTotal || 0) + 
    (usStocksTotal || 0) + 
    (cryptoTotal || 0)
  );
  
  // Use either real data or placeholder data
  const isDataLoaded = assets.length > 0;
  
  // Helper for formatting currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };
  
  // Simplified data for display
  const assetData = [
    { name: 'Indian Stocks', purchase: indianStocksTotal || 0, current: indianStocksCurrentTotal || 0 },
    { name: 'US Stocks', purchase: usStocksTotal || 0, current: usStocksCurrentTotal || 0 },
    { name: 'Crypto', purchase: cryptoTotal || 0, current: cryptoCurrentTotal || 0 }
  ];
  
  // Demo data for empty state
  const demoData = [
    { name: 'Indian Stocks', purchase: 4000, current: 5000 },
    { name: 'US Stocks', purchase: 3000, current: 2800 },
    { name: 'Crypto', purchase: 2000, current: 3200 }
  ];

  const COLORS = {
    indian: theme.palette.primary.main,
    us: theme.palette.secondary.main,
    crypto: theme.palette.success.main
  };

  return (
    <Box sx={{ mt: 4, mb: 4, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      
      {/* First row - Portfolio Summary */}
      <Grid container spacing={3} sx={{ mb: 3, maxWidth: 1100, mx: 'auto' }}>
        <Grid item xs={12}>
          <Paper 
            elevation={3} 
            sx={{ 
              p: 3,
              borderRadius: 2,
              overflow: 'hidden',
              background: 'linear-gradient(to right bottom, #ffffff, #fcfcff)',
              boxShadow: 'rgba(58, 53, 65, 0.1) 0px 2px 10px 0px',
              width: '100%'
            }}
          >
            <Typography variant="h6" gutterBottom align="center" sx={{ mb: 3, fontWeight: 600 }}>
              Portfolio Summary
            </Typography>
            
            <Grid container spacing={3} sx={{ px: 1 }}>
              <Grid item xs={12} sm={6} md={3} sx={{ mb: 2 }}>
                <Box sx={{ 
                  p: 2.5, 
                  bgcolor: 'background.paper', 
                  borderRadius: 2,
                  border: `1px solid ${theme.palette.divider}`,
                  textAlign: 'center',
                  boxShadow: 'rgba(58, 53, 65, 0.1) 0px 2px 4px -2px',
                  transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-3px)',
                    boxShadow: 'rgba(58, 53, 65, 0.18) 0px 4px 8px -2px',
                  }
                }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Total Investment
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    {isDataLoaded 
                      ? formatCurrency(totalPurchaseValue) 
                      : `₹${demoData.reduce((sum, item) => sum + item.purchase, 0).toLocaleString()}`}
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ 
                  p: 2.5, 
                  bgcolor: 'background.paper', 
                  borderRadius: 2,
                  border: `1px solid ${theme.palette.divider}`,
                  textAlign: 'center',
                  boxShadow: 'rgba(58, 53, 65, 0.1) 0px 2px 4px -2px',
                  transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-3px)',
                    boxShadow: 'rgba(58, 53, 65, 0.18) 0px 4px 8px -2px',
                  }
                }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Current Value
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    {isDataLoaded 
                      ? formatCurrency(totalPortfolioValue) 
                      : `₹${demoData.reduce((sum, item) => sum + item.current, 0).toLocaleString()}`}
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ 
                  p: 2.5, 
                  bgcolor: 'background.paper', 
                  borderRadius: 2,
                  border: `1px solid ${theme.palette.divider}`,
                  textAlign: 'center',
                  boxShadow: 'rgba(58, 53, 65, 0.1) 0px 2px 4px -2px',
                  transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-3px)',
                    boxShadow: 'rgba(58, 53, 65, 0.18) 0px 4px 8px -2px',
                  }
                }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Profit/Loss
                  </Typography>
                  <Typography 
                    variant="h6"
                    sx={{ 
                      fontWeight: 600,
                      color: isDataLoaded 
                        ? (totalPortfolioValue > totalPurchaseValue 
                            ? theme.palette.success.main 
                            : (totalPortfolioValue < totalPurchaseValue ? theme.palette.error.main : 'inherit'))
                        : theme.palette.success.main  // For demo data
                    }}>
                    {isDataLoaded 
                      ? formatCurrency(totalPortfolioValue - totalPurchaseValue) 
                      : `₹${(demoData.reduce((sum, item) => sum + item.current, 0) - demoData.reduce((sum, item) => sum + item.purchase, 0)).toLocaleString()}`}
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ 
                  p: 2.5, 
                  bgcolor: 'background.paper', 
                  borderRadius: 2,
                  border: `1px solid ${theme.palette.divider}`,
                  textAlign: 'center',
                  boxShadow: 'rgba(58, 53, 65, 0.1) 0px 2px 4px -2px',
                  transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-3px)',
                    boxShadow: 'rgba(58, 53, 65, 0.18) 0px 4px 8px -2px',
                  }
                }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    % Return
                  </Typography>
                  <Typography 
                    variant="h6"
                    sx={{ 
                      fontWeight: 600,
                      color: isDataLoaded 
                        ? (totalPortfolioValue > totalPurchaseValue 
                            ? theme.palette.success.main 
                            : (totalPortfolioValue < totalPurchaseValue ? theme.palette.error.main : 'inherit'))
                        : theme.palette.success.main  // For demo data
                    }}>
                    {isDataLoaded && totalPurchaseValue > 0
                      ? `${(((totalPortfolioValue - totalPurchaseValue) / totalPurchaseValue) * 100).toFixed(2)}%`
                      : '+8.33%' // Demo data
                    }
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>

      {/* Second row - Charts */}
      <Grid container spacing={3} sx={{ maxWidth: 1100, mx: 'auto' }}>
        {/* Asset Allocation Summary */}
        <Grid item xs={12} md={6}>
          <Paper 
            elevation={3} 
            sx={{ 
              p: 3, 
              minHeight: 300,
              borderRadius: 2,
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column',
              boxShadow: 'rgba(58, 53, 65, 0.1) 0px 2px 10px 0px',
              background: 'linear-gradient(to right bottom, #ffffff, #fcfcff)'
            }}
          >
            <Typography variant="h6" align="center" gutterBottom>
              Current Asset Allocation
            </Typography>
            
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px' }}>
                <CircularProgress />
              </Box>
            ) : (
              <Box sx={{ display: 'flex', flexDirection: 'column', flexGrow: 1, justifyContent: 'center', px: 1 }}>
                <Box sx={{ mb: 2, pb: 2, borderBottom: `1px dashed ${theme.palette.divider}` }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom sx={{ fontWeight: 500 }}>
                    Asset Distribution
                  </Typography>
                </Box>
                
                {/* Display simplified allocation blocks */}
                {(isDataLoaded ? assetData : demoData)
                  .filter(item => item.current > 0)
                  .map((item, index) => {
                    const percentage = isDataLoaded 
                      ? ((item.current / (totalPortfolioValue || 1)) * 100).toFixed(1)
                      : (item.name === 'Indian Stocks' ? 40 : (item.name === 'US Stocks' ? 30 : 30));
                    
                    return (
                      <Box key={index} sx={{ mb: 3 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5, alignItems: 'center' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Box 
                              sx={{ 
                                width: 12, 
                                height: 12, 
                                borderRadius: '50%', 
                                mr: 1,
                                bgcolor: item.name === 'Indian Stocks' 
                                  ? COLORS.indian 
                                  : (item.name === 'US Stocks' ? COLORS.us : COLORS.crypto),
                              }} 
                            />
                            <Typography variant="body2" fontWeight="medium">{item.name}</Typography>
                          </Box>
                          <Box sx={{ display: 'flex', alignItems: 'baseline' }}>
                            <Typography variant="body2" fontWeight="medium">
                              {isDataLoaded ? formatCurrency(item.current) : `₹${(item.name === 'Indian Stocks' ? 40000 : (item.name === 'US Stocks' ? 30000 : 30000)).toLocaleString()}`}
                            </Typography>
                            <Typography variant="caption" color="text.secondary" sx={{ ml: 0.5 }}>
                              ({percentage}%)
                            </Typography>
                          </Box>
                        </Box>
                        <Box sx={{ height: 10, bgcolor: theme.palette.grey[100], borderRadius: 5, overflow: 'hidden' }}>
                          <Box 
                            sx={{ 
                              height: '100%', 
                              width: `${percentage}%`,
                              bgcolor: item.name === 'Indian Stocks' 
                                ? COLORS.indian 
                                : (item.name === 'US Stocks' ? COLORS.us : COLORS.crypto),
                              borderRadius: 5,
                              transition: 'width 0.8s ease-in-out'
                            }}
                          />
                        </Box>
                      </Box>
                    );
                })}  
                
                {!isDataLoaded && (
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center', mt: 2 }}>
                    Demo data - Add assets to see your portfolio allocation
                  </Typography>
                )}
              </Box>
            )}
          </Paper>
        </Grid>
        
        {/* Purchase vs Current Value Comparison */}
        <Grid item xs={12} md={6}>
          <Paper 
            elevation={3} 
            sx={{ 
              p: 3, 
              minHeight: 300,
              borderRadius: 2,
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column',
              boxShadow: 'rgba(58, 53, 65, 0.1) 0px 2px 10px 0px',
              background: 'linear-gradient(to right bottom, #ffffff, #fcfcff)'
            }}
          >
            <Typography variant="h6" align="center" gutterBottom>
              Purchase vs Current Value
            </Typography>
            
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px' }}>
                <CircularProgress />
              </Box>
            ) : (
              <Box sx={{ display: 'flex', flexDirection: 'column', flexGrow: 1, justifyContent: 'center', px: 1 }}>
                <Box sx={{ mb: 2, pb: 2, borderBottom: `1px dashed ${theme.palette.divider}` }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom sx={{ fontWeight: 500 }}>
                    Investment Comparison
                  </Typography>
                </Box>
                
                {/* Header */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>Asset Type</Typography>
                  <Box sx={{ display: 'flex' }}>
                    <Typography variant="body2" color="text.secondary" sx={{ width: 110, textAlign: 'right', fontWeight: 500 }}>Purchase</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ width: 110, textAlign: 'right', ml: 2, fontWeight: 500 }}>Current</Typography>
                  </Box>
                </Box>
                
                {/* Data rows */}
                {(isDataLoaded ? assetData : demoData).map((item, index) => (
                  <Box key={index} sx={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    mb: 1.5,
                    p: 1.5,
                    bgcolor: index % 2 === 0 ? 'rgba(0,0,0,0.02)' : 'transparent',
                    borderRadius: 1,
                    border: `1px solid ${theme.palette.divider}`,
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      boxShadow: 1,
                      bgcolor: 'rgba(0,0,0,0.01)'
                    }
                  }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Box 
                        sx={{ 
                          width: 10, 
                          height: 10, 
                          borderRadius: '50%', 
                          mr: 1,
                          bgcolor: item.name === 'Indian Stocks' 
                            ? COLORS.indian 
                            : (item.name === 'US Stocks' ? COLORS.us : COLORS.crypto),
                        }} 
                      />
                      <Typography variant="body2" fontWeight="medium">{item.name}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex' }}>
                      <Typography variant="body2" sx={{ width: 110, textAlign: 'right' }}>
                        {isDataLoaded ? formatCurrency(item.purchase) : `₹${item.purchase.toLocaleString()}`}
                      </Typography>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          width: 110, 
                          textAlign: 'right',
                          ml: 2,
                          fontWeight: 'medium',
                          color: item.current > item.purchase 
                            ? theme.palette.success.main 
                            : (item.current < item.purchase ? theme.palette.error.main : 'inherit')
                        }}
                      >
                        {isDataLoaded ? formatCurrency(item.current) : `₹${item.current.toLocaleString()}`}
                      </Typography>
                    </Box>
                  </Box>
                ))}
                
                {/* Total */}
                <Box sx={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  mt: 3,
                  pt: 2,
                  borderTop: `1px solid ${theme.palette.divider}`,
                  bgcolor: 'rgba(0,0,0,0.02)',
                  p: 1.5,
                  borderRadius: 1,
                  border: `1px solid ${theme.palette.divider}`
                }}>
                  <Typography variant="subtitle2">Total Portfolio</Typography>
                  <Box sx={{ display: 'flex' }}>
                    <Typography variant="subtitle2" sx={{ width: 110, textAlign: 'right' }}>
                      {isDataLoaded 
                        ? formatCurrency(totalPurchaseValue) 
                        : `₹${demoData.reduce((sum, item) => sum + item.purchase, 0).toLocaleString()}`}
                    </Typography>
                    <Typography 
                      variant="subtitle2" 
                      sx={{ 
                        width: 110, 
                        textAlign: 'right', 
                        ml: 2,
                        color: isDataLoaded 
                          ? (totalPortfolioValue > totalPurchaseValue 
                              ? theme.palette.success.main 
                              : (totalPortfolioValue < totalPurchaseValue ? theme.palette.error.main : 'inherit'))
                          : theme.palette.success.main  // For demo data always show positive
                      }}
                    >
                      {isDataLoaded 
                        ? formatCurrency(totalPortfolioValue) 
                        : `₹${demoData.reduce((sum, item) => sum + item.current, 0).toLocaleString()}`}
                    </Typography>
                  </Box>
                </Box>
                
                {!isDataLoaded && (
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center', mt: 2 }}>
                    Demo data - Add assets to see your portfolio values
                  </Typography>
                )}
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default PortfolioCharts;
