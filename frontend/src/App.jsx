import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Layout/Sidebar'
import Header from './components/Layout/Header'
import DashboardPage from './components/Dashboard/DashboardPage'
import AnalyzePage from './components/Analyze/AnalyzePage'
import InfluencerList from './components/Influencer/InfluencerList'
import InfluencerReport from './components/Influencer/InfluencerReport'
import ComparePage from './components/Compare/ComparePage'

function App() {
  return (
    <div className="min-h-screen min-h-[100dvh] bg-bg-primary">
      <Header />

      <div className="hidden lg:block">
        <Sidebar />
      </div>

      <main
        className="p-5 lg:p-8 pb-28 lg:pb-8 lg:ml-60"
        style={{
          paddingTop: 'calc(env(safe-area-inset-top, 0px) + 72px)',
        }}
      >
        <div className="max-w-5xl mx-auto">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/analyze" element={<AnalyzePage />} />
            <Route path="/influencers" element={<InfluencerList />} />
            <Route path="/influencer/:id" element={<InfluencerReport />} />
            <Route path="/compare" element={<ComparePage />} />
          </Routes>
        </div>
      </main>

      <div className="lg:hidden">
        <Sidebar />
      </div>
    </div>
  )
}

export default App
