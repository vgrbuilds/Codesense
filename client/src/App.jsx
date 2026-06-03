import React, { useState, useEffect, useRef } from 'react';
import Mermaid from './components/Mermaid';

const API_BASE = 'http://localhost:8000';

function App() {
  // Navigation & Session State
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [user, setUser] = useState(null);
  const [view, setView] = useState('landing'); // 'landing', 'dashboard', 'project'
  const [authTab, setAuthTab] = useState('login'); // 'login', 'register'
  
  // Dashboard State
  const [projects, setProjects] = useState([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  
  // Form States
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [registerName, setRegisterName] = useState('');
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [projectName, setProjectName] = useState('');
  const [githubLink, setGithubLink] = useState('');
  
  // Project Details State
  const [selectedProject, setSelectedProject] = useState(null);
  const [repoDetails, setRepoDetails] = useState(null);
  const [conversation, setConversation] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [activeDiagramTab, setActiveDiagramTab] = useState('architecture'); // 'architecture', 'workflow', 'er'
  
  // Status States
  const [loading, setLoading] = useState(false);
  const [authError, setAuthError] = useState('');
  const [dashboardError, setDashboardError] = useState('');
  const [projectError, setProjectError] = useState('');
  const [sendingMessage, setSendingMessage] = useState(false);

  const messagesEndRef = useRef(null);

  // Initialize and validate token
  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
      fetchUserProfile(token);
    } else {
      localStorage.removeItem('token');
      setUser(null);
      setView('landing');
    }
  }, [token]);

  // Fetch projects when user state is loaded and we are on dashboard
  useEffect(() => {
    if (user && view === 'dashboard') {
      fetchUserProjects();
    }
  }, [user, view]);

  // Auto-scroll chat to bottom
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages]);

  const fetchUserProfile = async (authToken) => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/profile/me`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setUser(data);
        setView('dashboard');
      } else {
        // Token expired or invalid
        setToken('');
      }
    } catch (err) {
      console.error(err);
      setToken('');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setAuthError('');
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: loginEmail, password: loginPassword })
      });
      const data = await res.json();
      if (res.ok) {
        setToken(data.access_token);
        setLoginEmail('');
        setLoginPassword('');
      } else {
        setAuthError(data.detail || 'Login failed. Please check your credentials.');
      }
    } catch (err) {
      setAuthError('Unable to connect to the server.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setAuthError('');
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: registerName,
          email: registerEmail,
          password: registerPassword
        })
      });
      const data = await res.json();
      if (res.ok) {
        setToken(data.access_token);
        setRegisterName('');
        setRegisterEmail('');
        setRegisterPassword('');
      } else {
        setAuthError(data.detail || 'Registration failed. User may already exist.');
      }
    } catch (err) {
      setAuthError('Unable to connect to the server.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setToken('');
  };

  const fetchUserProjects = async () => {
    if (!user) return;
    try {
      setDashboardError('');
      const res = await fetch(`${API_BASE}/project/user/${user._id}`);
      if (res.ok) {
        const data = await res.json();
        setProjects(data);
      } else {
        setDashboardError('Failed to fetch projects.');
      }
    } catch (err) {
      setDashboardError('Unable to load projects from the database.');
    }
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    if (!projectName || !githubLink) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/project/?user_id=${user._id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: projectName,
          github_link: githubLink
        })
      });
      if (res.ok) {
        setIsCreateModalOpen(false);
        setProjectName('');
        setGithubLink('');
        fetchUserProjects();
        // Refresh credits as project creation triggers repo ingestion
        fetchUserProfile(token);
      } else {
        const data = await res.json();
        alert(data.detail || 'Failed to create project.');
      }
    } catch (err) {
      alert('Error creating project.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectProject = async (proj) => {
    setSelectedProject(proj);
    setRepoDetails(null);
    setConversation(null);
    setChatMessages([]);
    setProjectError('');
    setLoading(true);
    setView('project');

    try {
      // 1. Fetch Repository Details
      const repoRes = await fetch(`${API_BASE}/project/${proj._id}/repository`);
      if (!repoRes.ok) throw new Error('Failed to fetch repository metadata.');
      const repoData = await repoRes.json();
      setRepoDetails(repoData);

      // 2. Fetch Conversation History
      const chatRes = await fetch(`${API_BASE}/chat/${proj._id}`);
      if (!chatRes.ok) throw new Error('Failed to fetch conversation history.');
      const chatData = await chatRes.json();
      setConversation(chatData);
      setChatMessages(chatData.messages || []);
    } catch (err) {
      console.error(err);
      setProjectError(err.message || 'An error occurred loading project details.');
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!chatInput.trim() || !conversation || !selectedProject || sendingMessage) return;

    const text = chatInput.trim();
    setChatInput('');
    setSendingMessage(true);

    // Optimistically add user message to list
    const optimisticMessage = {
      _id: `temp-${Date.now()}`,
      conversation_id: conversation._id,
      role: 'user',
      content: text,
      created_at: new Date().toISOString()
    };
    setChatMessages(prev => [...prev, optimisticMessage]);

    try {
      const res = await fetch(`${API_BASE}/chat/${conversation._id}/message?repo_id=${selectedProject.repo_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ content: text })
      });

      if (res.ok) {
        const reply = await res.json();
        setChatMessages(prev => [...prev, reply]);
        // Refresh profile for credits count update
        fetchUserProfile(token);
      } else {
        const errorData = await res.json();
        const errorMessage = {
          _id: `err-${Date.now()}`,
          conversation_id: conversation._id,
          role: 'assistant',
          content: `⚠️ Failed to get reply: ${errorData.detail || 'Server error.'}`,
          created_at: new Date().toISOString()
        };
        setChatMessages(prev => [...prev, errorMessage]);
      }
    } catch (err) {
      const errorMessage = {
        _id: `err-${Date.now()}`,
        conversation_id: conversation._id,
        role: 'assistant',
        content: `⚠️ Network error. Could not reach the chatbot.`,
        created_at: new Date().toISOString()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setSendingMessage(false);
    }
  };

  // Rendering Helper for Diagram Tabs
  const getDiagramMarkup = () => {
    if (!repoDetails) return '';
    if (activeDiagramTab === 'architecture') return repoDetails.architecture_diagram;
    if (activeDiagramTab === 'workflow') return repoDetails.workflow_diagram;
    if (activeDiagramTab === 'er') return repoDetails.er_diagram;
    return '';
  };

  // Views rendering
  if (view === 'landing') {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="brand-header">
            <h1 className="brand-logo">Codesense</h1>
            <p className="brand-tagline">AI-powered code ingestion, architecture visualization, and chat</p>
          </div>
          
          <div className="auth-tabs">
            <button 
              className={`auth-tab-btn ${authTab === 'login' ? 'active' : ''}`}
              onClick={() => { setAuthTab('login'); setAuthError(''); }}
            >
              Sign In
            </button>
            <button 
              className={`auth-tab-btn ${authTab === 'register' ? 'active' : ''}`}
              onClick={() => { setAuthTab('register'); setAuthError(''); }}
            >
              Register
            </button>
          </div>

          {authError && <div className="auth-error">{authError}</div>}

          {authTab === 'login' ? (
            <form onSubmit={handleLogin}>
              <div className="form-group">
                <label className="form-label">Email Address</label>
                <input 
                  type="email" 
                  className="form-input" 
                  placeholder="name@domain.com"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  required 
                />
              </div>
              <div className="form-group">
                <label className="form-label">Password</label>
                <input 
                  type="password" 
                  className="form-input" 
                  placeholder="••••••••"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  required 
                />
              </div>
              <button type="submit" className="btn-primary" disabled={loading}>
                {loading ? 'Authenticating...' : 'Sign In'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleRegister}>
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="John Doe"
                  value={registerName}
                  onChange={(e) => setRegisterName(e.target.value)}
                  required 
                />
              </div>
              <div className="form-group">
                <label className="form-label">Email Address</label>
                <input 
                  type="email" 
                  className="form-input" 
                  placeholder="name@domain.com"
                  value={registerEmail}
                  onChange={(e) => setRegisterEmail(e.target.value)}
                  required 
                />
              </div>
              <div className="form-group">
                <label className="form-label">Password</label>
                <input 
                  type="password" 
                  className="form-input" 
                  placeholder="••••••••"
                  value={registerPassword}
                  onChange={(e) => setRegisterPassword(e.target.value)}
                  required 
                />
              </div>
              <button type="submit" className="btn-primary" disabled={loading}>
                {loading ? 'Creating Account...' : 'Register'}
              </button>
            </form>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Shared Navbar */}
      <nav className="navbar">
        <div className="nav-brand" onClick={() => setView('dashboard')}>
          Codesense
        </div>
        <div className="nav-actions">
          {user && (
            <div className="profile-widget" style={{ cursor: 'pointer' }} onClick={() => setIsProfileModalOpen(true)}>
              <span className="credits-badge">{user.credits} Credits</span>
              <div className="user-avatar">{user.name.charAt(0).toUpperCase()}</div>
              <span style={{ fontSize: '14px', fontWeight: '500' }}>{user.name}</span>
            </div>
          )}
          <button className="logout-btn" onClick={handleLogout}>Logout</button>
        </div>
      </nav>

      {/* View 1: Dashboard / Home */}
      {view === 'dashboard' && (
        <main className="dashboard-content">
          <div className="dashboard-header">
            <div className="dashboard-title">
              <h2>My Repositories</h2>
              <p>Select an ingested codebase to view structure diagrams and chat.</p>
            </div>
            <button className="btn-accent" onClick={() => setIsCreateModalOpen(true)}>
              + Ingest Repository
            </button>
          </div>

          {dashboardError && <div className="auth-error">{dashboardError}</div>}

          {projects.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">📂</div>
              <h3>No repositories ingested yet</h3>
              <p>Analyze your first GitHub codebase to map workflows, architecture, and interact with the codebase via AI.</p>
              <button className="btn-accent" onClick={() => setIsCreateModalOpen(true)}>
                Ingest GitHub Repository
              </button>
            </div>
          ) : (
            <div className="projects-grid">
              {projects.map((proj) => (
                <div 
                  key={proj._id} 
                  className="project-card"
                  onClick={() => handleSelectProject(proj)}
                >
                  <div className="project-card-header">
                    <h3>{proj.name}</h3>
                    <div className="project-card-link">{proj.github_link}</div>
                  </div>
                  <div className="project-card-footer">
                    <span className="project-date">
                      Ingested {new Date(proj.created_at).toLocaleDateString()}
                    </span>
                    <span className="project-action-indicator">
                      Explore →
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      )}

      {/* View 2: Project Details Page */}
      {view === 'project' && selectedProject && (
        <main className="project-details-container">
          
          {/* Pane 1: Left Sidebar Details */}
          <section className="metadata-sidebar">
            <div style={{ marginBottom: '8px' }}>
              <button className="btn-secondary" style={{ padding: '6px 12px', fontSize: '13px' }} onClick={() => setView('dashboard')}>
                ← Back to Dashboard
              </button>
            </div>
            
            <div className="metadata-section">
              <h2 style={{ fontSize: '22px', color: 'white', marginBottom: '4px' }}>{selectedProject.name}</h2>
              <a 
                href={selectedProject.github_link} 
                target="_blank" 
                rel="noreferrer" 
                style={{ fontSize: '12px', color: 'var(--color-accent)', textDecoration: 'none', wordBreak: 'break-all' }}
              >
                🔗 GitHub Link
              </a>
            </div>

            {loading && !repoDetails && (
              <div className="loading-diagram">Loading repository summary...</div>
            )}

            {projectError && <div className="auth-error">{projectError}</div>}

            {repoDetails && (
              <>
                <div className="metadata-section">
                  <h4>Summary</h4>
                  <p style={{ fontSize: '14px', lineHeight: '1.5', color: 'var(--text-secondary)' }}>
                    {repoDetails.summary || repoDetails.description}
                  </p>
                </div>

                <div className="metadata-section">
                  <h4>Technologies</h4>
                  <div className="tech-tags">
                    {repoDetails.technologies && repoDetails.technologies.map((t, idx) => (
                      <span key={idx} className="tech-tag">{t}</span>
                    ))}
                  </div>
                </div>

                <div className="metadata-section">
                  <h4>Setup Guide</h4>
                  <div className="setup-guide-box">
                    {repoDetails.setup_guide || 'No local setup instructions generated.'}
                  </div>
                </div>
              </>
            )}
          </section>

          {/* Pane 2: Middle Diagram Visualizer */}
          <section className="diagram-pane">
            <div className="diagram-tabs">
              <button 
                className={`diagram-tab-btn ${activeDiagramTab === 'architecture' ? 'active' : ''}`}
                onClick={() => setActiveDiagramTab('architecture')}
              >
                System Architecture
              </button>
              <button 
                className={`diagram-tab-btn ${activeDiagramTab === 'workflow' ? 'active' : ''}`}
                onClick={() => setActiveDiagramTab('workflow')}
              >
                Main Workflow
              </button>
              <button 
                className={`diagram-tab-btn ${activeDiagramTab === 'er' ? 'active' : ''}`}
                onClick={() => setActiveDiagramTab('er')}
              >
                Database Models (ER)
              </button>
            </div>

            <div className="diagram-canvas">
              {loading && !repoDetails && (
                <div className="loading-diagram">Building visual model mapping...</div>
              )}
              {repoDetails && (
                <Mermaid chart={getDiagramMarkup()} />
              )}
            </div>
          </section>

          {/* Pane 3: Right Sidebar Chat Interface */}
          <section className="chat-sidebar">
            <div className="chat-header">
              <div style={{ fontSize: '20px' }}>🤖</div>
              <div>
                <h4>Codesense Chatbot</h4>
                <p style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>Answers questions regarding this codebase</p>
              </div>
            </div>

            <div className="chat-history">
              {chatMessages.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '40px 10px', color: 'var(--text-muted)', fontSize: '13px' }}>
                  Ask a question to start. For example:<br/>
                  <em>"What is the system design?"</em> or <br/>
                  <em>"How is authentication configured?"</em>
                </div>
              ) : (
                chatMessages.map((msg) => (
                  <div key={msg._id} className={`chat-message ${msg.role}`}>
                    {msg.content}
                  </div>
                ))
              )}
              {sendingMessage && (
                <div className="chat-message assistant" style={{ fontStyle: 'italic', color: 'var(--text-muted)' }}>
                  Thinking...
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="chat-input-area">
              <form onSubmit={handleSendMessage} className="chat-input-form">
                <input 
                  type="text" 
                  className="chat-text-input" 
                  placeholder="Ask a question about this code..."
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  disabled={sendingMessage || !conversation}
                  required
                />
                <button type="submit" className="chat-send-btn" disabled={sendingMessage || !conversation || !chatInput.trim()}>
                  Send
                </button>
              </form>
            </div>
          </section>

        </main>
      )}

      {/* Modal 1: Ingest Repo / Create Project */}
      {isCreateModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Ingest Codebase</h3>
              <button className="modal-close" onClick={() => setIsCreateModalOpen(false)}>×</button>
            </div>
            <form onSubmit={handleCreateProject}>
              <div className="form-group">
                <label className="form-label">Project Name</label>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="My API Service"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  required 
                />
              </div>
              <div className="form-group">
                <label className="form-label">GitHub Repository Link</label>
                <input 
                  type="url" 
                  className="form-input" 
                  placeholder="https://github.com/owner/repository"
                  value={githubLink}
                  onChange={(e) => setGithubLink(e.target.value)}
                  required 
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setIsCreateModalOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-accent" disabled={loading}>
                  {loading ? 'Ingesting...' : 'Start Ingestion'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal 2: User Profile Details */}
      {isProfileModalOpen && user && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>My Profile</h3>
              <button className="modal-close" onClick={() => setIsProfileModalOpen(false)}>×</button>
            </div>
            <div className="profile-modal-body">
              <div className="profile-stat">
                <span>Name</span>
                <span className="profile-stat-value">{user.name}</span>
              </div>
              <div className="profile-stat">
                <span>Email</span>
                <span className="profile-stat-value">{user.email}</span>
              </div>
              <div className="profile-stat">
                <span>Available AI Credits</span>
                <span className="profile-stat-value" style={{ color: 'var(--color-success)' }}>{user.credits}</span>
              </div>
              <div className="profile-stat">
                <span>Account Created</span>
                <span className="profile-stat-value">{new Date(user.created_at).toLocaleDateString()}</span>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setIsProfileModalOpen(false)}>
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
