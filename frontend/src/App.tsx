import { Sidebar } from "./components/Sidebar";
import { MessageList } from "./components/Chat";
import { ChatInput } from "./components/Input/ChatInput";
import { ModeInitializer } from "./components/ModeInitializer";
import "./styles/globals.css";

function App() {
    return (
        <div className="app-bg h-screen w-screen overflow-hidden flex">
            {/* ModeInitializer - handles session loading on mode change */}
            <ModeInitializer />
            
            {/* 侧边栏 - 固定高度 */}
            <Sidebar />
            
            {/* 主内容区 - flex布局，高度固定 */}
            <main className="flex-1 flex flex-col ml-[260px] h-full overflow-hidden">
                {/* 消息列表区域 - 独立滚动 */}
                <div className="flex-1 overflow-y-auto p-4 sm:p-6">
                    <div className="max-w-4xl mx-auto min-h-full">
                        <MessageList />
                    </div>
                </div>
                
                {/* 输入框 - 固定在底部 */}
                <ChatInput />
            </main>
        </div>
    );
}

export default App;
