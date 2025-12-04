import React from 'react';
import Sidebar from './components/Sidebar';
import Toolbar from './components/Toolbar';
import HierarchyTree from './components/HierarchyTree';
import PDFViewer from './components/PDFViewer';
import PDFViewerModal from './components/PDFViewerModal';
import JSONViewer from './components/Tabs/JSONViewer';
import TablesViewer from './components/Tabs/TablesViewer';
import ImagesViewer from './components/Tabs/ImagesViewer';
import SummaryKeywords from './components/Tabs/SummaryKeywords';
import { useStore } from './store/useStore';
import { FileText, List, Code, Table, Image as ImageIcon, Sparkles } from 'lucide-react';
import clsx from 'clsx';

function App() {
  const { activeTab, setActiveTab, sidebarOpen } = useStore();

  const tabs = [
    { id: 'summary', label: 'Summary', icon: Sparkles },
    { id: 'hierarchy', label: 'Hierarchy', icon: List },
    { id: 'json', label: 'JSON', icon: Code },
    { id: 'tables', label: 'Tables', icon: Table },
    { id: 'images', label: 'Images', icon: ImageIcon },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'summary': return <SummaryKeywords />;
      case 'hierarchy': return <HierarchyTree />;
      case 'json': return <JSONViewer />;
      case 'tables': return <TablesViewer />;
      case 'images': return <ImagesViewer />;
      default: return <SummaryKeywords />;
    }
  };

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden font-sans">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0">
        <Toolbar />

        <div className="flex-1 flex overflow-hidden">
          {/* Right Panel - Main Content */}
          <div className="flex-1 flex flex-col min-w-0 bg-secondary/10">
            {/* Tabs Header */}
            <div className="flex items-center gap-1 px-4 pt-3 border-b border-border bg-background">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={clsx(
                      "flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-t-md transition-colors border-t border-x border-transparent mb-[-1px]",
                      activeTab === tab.id
                        ? "bg-secondary/10 border-border border-b-secondary/10 text-primary"
                        : "text-muted-foreground hover:text-foreground hover:bg-accent"
                    )}
                  >
                    <Icon size={14} />
                    {tab.label}
                  </button>
                );
              })}
            </div>

            {/* Tab Content */}
            <div className="flex-1 overflow-hidden relative">
              {renderContent()}
            </div>
          </div>
        </div>
      </div>
      
      {/* PDF Viewer Modal */}
      <PDFViewerModal />
    </div>
  );
}

export default App;
