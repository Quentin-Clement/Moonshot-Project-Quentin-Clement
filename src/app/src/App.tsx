import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ResultsPage from './pages/ResultsPage';
import Layout from './components/Layout';
import SegmentPage from './pages/SegmentPage';
import { VideoProvider } from './context/VideoContext';

function App() {
  return (
    <VideoProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Layout><HomePage /></Layout>} />
          <Route path="/results" element={<Layout><ResultsPage /></Layout>} />
          <Route path="/segment/:id" element={<Layout><SegmentPage /></Layout>} />
        </Routes>
      </Router>
    </VideoProvider>
  );
}

export default App;