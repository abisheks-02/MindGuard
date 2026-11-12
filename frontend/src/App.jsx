import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import AnalyzePage from './pages/AnalyzePage';
import JourneyPage from './pages/JourneyPage';
import RecoveryPage from './pages/RecoveryPage';
import AboutPage from './pages/AboutPage';
import OnboardingPage from './pages/OnboardingPage';
import ToolsPage from './pages/ToolsPage';
import SettingsPage from './pages/SettingsPage';
import CrisisPage from './pages/CrisisPage';
import ClinicalDashboard from './pages/ClinicalDashboard';
import InterventionPage from './pages/InterventionPage';
import DiscoverPage from './pages/DiscoverPage';
import ReflectionPage from './pages/ReflectionPage';
import { useStore } from './store/useStore';

function App() {
  const { onboardingComplete, crisisModeActive } = useStore();

  return (
    <Router>
      {!onboardingComplete ? (
        <Routes>
          <Route path="*" element={<OnboardingPage />} />
        </Routes>
      ) : (
        <Layout>
          <Routes>
            <Route path="/" element={<AnalyzePage />} />
            <Route path="/journey" element={<JourneyPage />} />
            <Route path="/tools" element={<ToolsPage />} />
            <Route path="/intervention" element={<InterventionPage />} />
            <Route path="/discover" element={<DiscoverPage />} />
            <Route path="/reflection" element={<ReflectionPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/dashboard" element={<ClinicalDashboard />} />
          </Routes>
        </Layout>
      )}
      {crisisModeActive && <CrisisPage />}
    </Router>
  );
}

export default App;
