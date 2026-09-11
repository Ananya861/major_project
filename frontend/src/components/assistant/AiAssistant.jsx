import React, { useState, useEffect, useRef, useMemo } from 'react';
import {
  Bot,
  X,
  Send,
  Sparkles,
  Minimize2,
  Maximize2,
  Trash2,
  ChevronDown,
  ChevronUp,
  Leaf,
  Loader2,
  User,
  Info,
} from 'lucide-react';
import { useTranslation } from '../../i18n/LanguageContext';
import { useFarm } from '../../context/FarmContext';
import { assistantService } from '../../services/assistantService';

const AiAssistant = () => {
  const { t, language, currentLanguage } = useTranslation();
  const { selectedFarm } = useFarm();

  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [showContextDetails, setShowContextDetails] = useState(false);

  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Build active farm context
  const farmContext = useMemo(() => {
    if (!selectedFarm) return null;
    const soil = selectedFarm.latest_soil || {};
    return {
      farm_id: selectedFarm.farm_id,
      farm_name: `Farm #${selectedFarm.farm_id}`,
      latitude: selectedFarm.latitude,
      longitude: selectedFarm.longitude,
      area_acres: selectedFarm.area_acres,
      soil_ph: soil.ph ?? null,
      nitrogen: soil.nitrogen ?? null,
      phosphorus: soil.phosphorus ?? null,
      potassium: soil.potassium ?? null,
      moisture: soil.moisture ?? null,
      soil_type: soil.soil_type ?? null,
    };
  }, [selectedFarm]);

  // Reset or update welcome greeting when language changes or on mount
  useEffect(() => {
    const welcome = t(
      'assistant.welcomeGreeting',
      'Hello Farmer! I am your AgriSmart AI Assistant. How can I assist with your crops, soil, weather, or mandi prices today?'
    );

    setMessages((prev) => {
      // If empty, initialize
      if (prev.length === 0) {
        return [{ id: 'welcome-1', sender: 'assistant', text: welcome, time: new Date() }];
      }
      // If only welcome message exists, update it to the new language
      if (prev.length === 1 && prev[0].id === 'welcome-1') {
        return [{ id: 'welcome-1', sender: 'assistant', text: welcome, time: prev[0].time }];
      }
      return prev;
    });

    // Fetch language-specific suggestions
    let isMounted = true;
    assistantService
      .getSuggestions(language)
      .then((data) => {
        if (isMounted && data.suggestions) {
          setSuggestions(data.suggestions);
        }
      })
      .catch(() => {});

    return () => {
      isMounted = false;
    };
  }, [language, t]);

  // Scroll to bottom of message list
  useEffect(() => {
    if (isOpen && !isMinimized) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, loading, isOpen, isMinimized]);

  // Auto-focus input when opened
  useEffect(() => {
    if (isOpen && !isMinimized) {
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen, isMinimized]);

  const handleSendMessage = async (customText = null) => {
    const textToSend = (customText || inputMessage).trim();
    if (!textToSend || loading) return;

    const userMsgId = `user-${Date.now()}`;
    const newMessages = [
      ...messages,
      { id: userMsgId, sender: 'user', text: textToSend, time: new Date() },
    ];

    setMessages(newMessages);
    setInputMessage('');
    setLoading(true);

    try {
      const result = await assistantService.sendMessage(
        textToSend,
        language,
        farmContext
      );

      setMessages((prev) => [
        ...prev,
        {
          id: `ai-${Date.now()}`,
          sender: 'assistant',
          text: result.response,
          time: new Date(),
          contextUsed: result.context_used,
        },
      ]);

      if (result.suggestions && result.suggestions.length > 0) {
        setSuggestions(result.suggestions);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          sender: 'assistant',
          text:
            language === 'kn'
              ? 'ಕ್ಷಮಿಸಿ, ಪ್ರತಿಕ್ರಿಯೆ ಪಡೆಯಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೊಮ್ಮೆ ಪ್ರಯತ್ನಿಸಿ.'
              : language === 'hi'
              ? 'क्षमा करें, प्रतिक्रिया प्राप्त नहीं हो सकी। कृपया पुनः प्रयास करें।'
              : 'Sorry, could not process your request at this moment. Please try again.',
          time: new Date(),
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    const welcome = t(
      'assistant.welcomeGreeting',
      'Hello Farmer! I am your AgriSmart AI Assistant. How can I assist with your crops, soil, weather, or mandi prices today?'
    );
    setMessages([{ id: 'welcome-1', sender: 'assistant', text: welcome, time: new Date() }]);
  };

  // Helper to format text with bullet points and bold markings
  const renderMessageContent = (text) => {
    if (!text) return null;
    const lines = text.split('\n');
    return (
      <div className="space-y-1.5 text-xs leading-relaxed">
        {lines.map((line, idx) => {
          if (!line.trim()) return <div key={idx} className="h-1" />;

          // Parse markdown-like **bold**
          const parts = line.split(/(\*\*.*?\*\*)/g);
          const parsedLine = parts.map((part, pIdx) => {
            if (part.startsWith('**') && part.endsWith('**')) {
              return (
                <strong key={pIdx} className="font-bold text-slate-900">
                  {part.slice(2, -2)}
                </strong>
              );
            }
            return part;
          });

          if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
            return (
              <div key={idx} className="flex items-start space-x-1.5 pl-1">
                <span className="text-agri-600 font-bold shrink-0">•</span>
                <span className="flex-1">{parsedLine}</span>
              </div>
            );
          }

          return <p key={idx}>{parsedLine}</p>;
        })}
      </div>
    );
  };

  return (
    <>
      {/* Floating Trigger Button */}
      {!isOpen && (
        <div className="fixed bottom-5 right-5 z-40">
          <button
            onClick={() => {
              setIsOpen(true);
              setIsMinimized(false);
            }}
            className="group relative flex items-center space-x-2.5 px-4 py-3 bg-gradient-to-r from-agri-600 to-emerald-600 hover:from-agri-700 hover:to-emerald-700 text-white rounded-full shadow-lg shadow-agri-600/30 hover:shadow-xl hover:shadow-agri-600/40 hover:-translate-y-0.5 transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-agri-500/30"
            aria-label={t('assistant.buttonLabel', 'Agri AI Assistant')}
          >
            <div className="relative">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                <Bot className="w-5 h-5 text-white animate-pulse" />
              </div>
              <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-300 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-amber-400"></span>
              </span>
            </div>
            <div className="text-left hidden sm:block">
              <div className="text-xs font-extrabold tracking-tight leading-tight">
                {t('assistant.buttonLabel', 'Agri AI Assistant')}
              </div>
              <div className="text-[10px] text-agri-100 font-medium leading-tight">
                {currentLanguage?.nativeName || 'English'}
              </div>
            </div>
          </button>
        </div>
      )}

      {/* Floating / Popover Chat Window */}
      {isOpen && (
        <div
          className={`fixed z-50 transition-all duration-200 shadow-2xl ${
            isMinimized
              ? 'bottom-5 right-5 w-72 bg-white rounded-2xl border border-slate-200 overflow-hidden'
              : 'bottom-0 right-0 sm:bottom-5 sm:right-5 w-full sm:w-[420px] h-[85vh] sm:h-[600px] max-h-[92vh] bg-white rounded-t-3xl sm:rounded-3xl border border-slate-200/90 flex flex-col overflow-hidden'
          }`}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-agri-700 via-agri-600 to-emerald-700 text-white px-4 py-3 flex items-center justify-between shadow-xs">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-xl bg-white/15 flex items-center justify-center backdrop-blur-xs">
                <Sparkles className="w-4 h-4 text-amber-300" />
              </div>
              <div>
                <h3 className="text-xs font-bold tracking-tight">
                  {t('assistant.modalTitle', 'AgriSmart AI Assistant')}
                </h3>
                <div className="flex items-center space-x-1.5 text-[10px] text-agri-100">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-300 inline-block animate-pulse" />
                  <span>{currentLanguage?.nativeName || 'English'}</span>
                  <span>•</span>
                  <span>
                    {selectedFarm
                      ? `Farm #${selectedFarm.farm_id} (${selectedFarm.area_acres} ac)`
                      : t('assistant.generalMode', 'General Advisory')}
                  </span>
                </div>
              </div>
            </div>

            {/* Header Actions */}
            <div className="flex items-center space-x-1 text-white/80">
              <button
                onClick={handleClearChat}
                title={t('assistant.clearChat', 'Clear Conversation')}
                className="p-1.5 hover:text-white hover:bg-white/10 rounded-lg transition"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setIsMinimized((prev) => !prev)}
                className="p-1.5 hover:text-white hover:bg-white/10 rounded-lg transition hidden sm:block"
                title={isMinimized ? 'Expand' : 'Minimize'}
              >
                {isMinimized ? (
                  <Maximize2 className="w-3.5 h-3.5" />
                ) : (
                  <Minimize2 className="w-3.5 h-3.5" />
                )}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 hover:text-white hover:bg-white/10 rounded-lg transition"
                title={t('common.close', 'Close')}
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Minimized Body (Just header shown) */}
          {!isMinimized && (
            <>
              {/* Context Summary Collapsible Bar */}
              {selectedFarm && (
                <div className="bg-slate-50 border-b border-slate-100 px-3.5 py-1.5 text-[11px] text-slate-600">
                  <button
                    onClick={() => setShowContextDetails((prev) => !prev)}
                    className="w-full flex items-center justify-between font-medium text-slate-700 hover:text-agri-700 transition"
                  >
                    <span className="flex items-center space-x-1.5">
                      <Leaf className="w-3.5 h-3.5 text-agri-600" />
                      <span>
                        {t('assistant.farmContextChip', 'Farm Context')}: Farm #{selectedFarm.farm_id}
                      </span>
                    </span>
                    <span className="flex items-center space-x-1 text-[10px] text-slate-400">
                      <span>{showContextDetails ? 'Hide' : 'View soil NPK'}</span>
                      {showContextDetails ? (
                        <ChevronUp className="w-3 h-3" />
                      ) : (
                        <ChevronDown className="w-3 h-3" />
                      )}
                    </span>
                  </button>

                  {showContextDetails && (
                    <div className="mt-2 p-2 bg-white rounded-xl border border-slate-200/70 text-[10px] space-y-1 text-slate-600 animate-fadeIn">
                      <div className="grid grid-cols-2 gap-1.5">
                        <div>
                          <span className="text-slate-400">Nitrogen (N):</span>{' '}
                          <strong className="text-slate-800">
                            {selectedFarm.latest_soil?.nitrogen ?? 'N/A'} kg/ha
                          </strong>
                        </div>
                        <div>
                          <span className="text-slate-400">Phosphorus (P):</span>{' '}
                          <strong className="text-slate-800">
                            {selectedFarm.latest_soil?.phosphorus ?? 'N/A'} kg/ha
                          </strong>
                        </div>
                        <div>
                          <span className="text-slate-400">Potassium (K):</span>{' '}
                          <strong className="text-slate-800">
                            {selectedFarm.latest_soil?.potassium ?? 'N/A'} kg/ha
                          </strong>
                        </div>
                        <div>
                          <span className="text-slate-400">pH / Moisture:</span>{' '}
                          <strong className="text-slate-800">
                            {selectedFarm.latest_soil?.ph ?? '--'} pH •{' '}
                            {selectedFarm.latest_soil?.moisture ?? '--'}%
                          </strong>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Message History */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50/40">
                {messages.map((msg) => {
                  const isUser = msg.sender === 'user';
                  return (
                    <div
                      key={msg.id}
                      className={`flex items-start space-x-2 ${
                        isUser ? 'flex-row-reverse space-x-reverse' : ''
                      }`}
                    >
                      {/* Avatar */}
                      <div
                        className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5 text-white text-[10px] font-bold ${
                          isUser
                            ? 'bg-slate-700'
                            : 'bg-gradient-to-br from-agri-600 to-emerald-600 shadow-xs'
                        }`}
                      >
                        {isUser ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
                      </div>

                      {/* Bubble */}
                      <div
                        className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 shadow-xs ${
                          isUser
                            ? 'bg-agri-600 text-white rounded-tr-xs'
                            : 'bg-white border border-slate-200/80 text-slate-800 rounded-tl-xs'
                        }`}
                      >
                        {renderMessageContent(msg.text)}

                        <div
                          className={`text-[9px] mt-1 text-right ${
                            isUser ? 'text-white/70' : 'text-slate-400'
                          }`}
                        >
                          {new Date(msg.time).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </div>
                      </div>
                    </div>
                  );
                })}

                {/* Loading indicator */}
                {loading && (
                  <div className="flex items-start space-x-2">
                    <div className="w-6 h-6 rounded-full bg-agri-600 flex items-center justify-center text-white shrink-0 mt-0.5">
                      <Bot className="w-3.5 h-3.5 animate-pulse" />
                    </div>
                    <div className="bg-white border border-slate-200/80 rounded-2xl rounded-tl-xs px-3.5 py-2.5 shadow-xs text-xs text-slate-500 flex items-center space-x-2">
                      <Loader2 className="w-3.5 h-3.5 text-agri-600 animate-spin" />
                      <span>{t('assistant.thinking', 'Analyzing farm data...')}</span>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Suggestions Prompt Chips */}
              {suggestions.length > 0 && (
                <div className="px-3 py-2 bg-white border-t border-slate-100 flex items-center space-x-1.5 overflow-x-auto no-scrollbar">
                  {suggestions.slice(0, 3).map((sugg, i) => (
                    <button
                      key={i}
                      onClick={() => handleSendMessage(sugg)}
                      disabled={loading}
                      className="shrink-0 text-[11px] font-medium px-2.5 py-1 bg-slate-50 hover:bg-agri-50 text-slate-700 hover:text-agri-700 rounded-full border border-slate-200/80 hover:border-agri-300 transition"
                    >
                      {sugg}
                    </button>
                  ))}
                </div>
              )}

              {/* Chat Input Bar */}
              <div className="p-3 bg-white border-t border-slate-200">
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSendMessage();
                  }}
                  className="flex items-center space-x-2"
                >
                  <input
                    ref={inputRef}
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder={t(
                      'assistant.inputPlaceholder',
                      'Ask in your language (e.g. soil NPK, crop advice, MSP)...'
                    )}
                    disabled={loading}
                    className="flex-1 px-3.5 py-2 text-xs border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500 bg-slate-50/50"
                  />
                  <button
                    type="submit"
                    disabled={!inputMessage.trim() || loading}
                    className="p-2 bg-agri-600 hover:bg-agri-700 text-white rounded-xl shadow-xs transition disabled:opacity-40"
                    title={t('assistant.sendBtn', 'Send')}
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </form>
              </div>
            </>
          )}
        </div>
      )}
    </>
  );
};

export default AiAssistant;
