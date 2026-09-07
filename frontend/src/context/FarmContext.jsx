import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { farmService } from '../services/farmService';
import { useAuth } from './AuthContext';

const FarmContext = createContext(null);

export const FarmProvider = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [farms, setFarms] = useState([]);
  const [loadingFarms, setLoadingFarms] = useState(false);
  const [errorFarms, setErrorFarms] = useState(null);
  const [selectedFarmId, setSelectedFarmId] = useState(null);

  const fetchFarms = useCallback(async () => {
    if (!isAuthenticated) {
      setFarms([]);
      setSelectedFarmId(null);
      return;
    }

    setLoadingFarms(true);
    setErrorFarms(null);
    try {
      const data = await farmService.listFarms();
      setFarms(data);
      if (data.length > 0) {
        setSelectedFarmId((prev) => (prev ? prev : data[0].farm_id));
      }
    } catch (err) {
      setErrorFarms(err.friendlyMessage || 'Failed to load farms');
    } finally {
      setLoadingFarms(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    fetchFarms();
  }, [fetchFarms]);

  const selectedFarm = farms.find((f) => f.farm_id === Number(selectedFarmId)) || farms[0] || null;

  return (
    <FarmContext.Provider
      value={{
        farms,
        loadingFarms,
        errorFarms,
        selectedFarmId,
        setSelectedFarmId,
        selectedFarm,
        refreshFarms: fetchFarms,
      }}
    >
      {children}
    </FarmContext.Provider>
  );
};

export const useFarm = () => {
  const context = useContext(FarmContext);
  if (!context) {
    throw new Error('useFarm must be used within a FarmProvider');
  }
  return context;
};
