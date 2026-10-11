import React, { useState } from 'react';
import { AppLayout } from './layouts/AppLayout';
import { NavTab } from './components/layout/Navigation';
import { OverviewPage } from './pages/OverviewPage';
import { FireRiskPage } from './pages/FireRiskPage';
import { ActiveFiresPage } from './pages/ActiveFiresPage';
import { SimulationPage } from './pages/SimulationPage';
import { LayersPage } from './pages/LayersPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { useRegions } from './features/regions/hooks/useRegions';
import { IgnitionPoint } from './types/domain';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<NavTab>('overview');
  const [prefilledIgnition, setPrefilledIgnition] = useState<IgnitionPoint | null>(null);
  const {
    regions,
    selectedRegionId,
    setSelectedRegionId,
    selectedRegion,
    boundary,
    isLoading: isLoadingRegions,
  } = useRegions();

  const handleNavigateToSimulation = (ignition?: IgnitionPoint) => {
    if (ignition) {
      setPrefilledIgnition(ignition);
    }
    setCurrentTab('simulation');
  };

  const renderActivePage = () => {
    switch (currentTab) {
      case 'overview':
        return (
          <OverviewPage
            regions={regions}
            selectedRegion={selectedRegion}
            boundary={boundary}
            onNavigateTab={setCurrentTab}
          />
        );
      case 'risk':
        return (
          <FireRiskPage
            selectedRegion={selectedRegion}
            boundary={boundary}
            onNavigateToSimulation={handleNavigateToSimulation}
          />
        );
      case 'active_fires':
        return (
          <ActiveFiresPage
            selectedRegion={selectedRegion}
            boundary={boundary}
            onNavigateToSimulation={handleNavigateToSimulation}
          />
        );
      case 'simulation':
        return (
          <SimulationPage
            selectedRegion={selectedRegion}
            boundary={boundary}
            initialIgnition={prefilledIgnition}
          />
        );
      case 'layers':
        return (
          <LayersPage
            selectedRegion={selectedRegion}
            boundary={boundary}
          />
        );
      default:
        return <NotFoundPage onReturnHome={() => setCurrentTab('overview')} />;
    }
  };

  return (
    <AppLayout
      currentTab={currentTab}
      onSelectTab={setCurrentTab}
      regions={regions}
      selectedRegionId={selectedRegionId}
      onSelectRegion={setSelectedRegionId}
      isLoadingRegions={isLoadingRegions}
      selectedRegion={selectedRegion}
    >
      {renderActivePage()}
    </AppLayout>
  );
};

export default App;
