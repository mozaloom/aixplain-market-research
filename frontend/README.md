# Market Research Frontend

React-based web interface for the Market Research Team Agent.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Backend API running (see ../backend/README.md)

### Installation

1. **Install dependencies:**
```bash
npm install
```

2. **Set environment variables:**
Create a `.env` file:
```bash
REACT_APP_API_URL=http://localhost:8000
```

### Development

```bash
# Start development server
npm start
```

The app will be available at: http://localhost:3000

### Production Build

```bash
# Build for production
npm run build

# Serve production build locally
npm install -g serve
serve -s build
```

## 🎨 Features

### Market Research Interface
- **Query Input** - Enter any market research question or product comparison
- **Real-time Progress** - Watch AI agents work in real-time
- **Interactive Results** - View analysis results with structured sections
- **Download Options** - Get reports in PDF, Markdown, or Citations JSON

### Agent Status Display
- **5 Specialized Agents** - Visual progress indicators for each agent
- **Live Updates** - Real-time status updates during analysis
- **Error Handling** - Clear error messages and retry options

### Report Features
- **Executive Summary** - Key insights and recommendations
- **Clickable Citations** - Source links that open in new tabs
- **Export Options** - Multiple download formats
- **Responsive Design** - Works on desktop and mobile

## 🏗️ Architecture

### Component Structure
```
src/
├── App.js              # Main application component
├── index.js            # React entry point
├── index.css           # Global styles (Tailwind)
└── components/         # Reusable components (future)
```

### Key Features

1. **Real-time Analysis** - Polls backend for job status updates
2. **Progress Tracking** - Shows which agents are active/completed
3. **Citation Handling** - Extracts and displays clickable source links
4. **Download Management** - Handles multiple file format downloads
5. **Error Recovery** - Graceful handling of analysis failures

## 🎨 Styling

### Tailwind CSS
The app uses Tailwind CSS for styling with a custom configuration:

- **Primary Colors** - Blue theme for professional look
- **Component Classes** - Reusable styles for buttons, cards, inputs
- **Responsive Design** - Mobile-first approach
- **Animation** - Loading states and transitions

### Key Style Classes
- `.btn-primary` - Primary action buttons
- `.card` - Container cards with shadow
- `.input-field` - Form input styling

## 🔌 API Integration

### Backend Communication
- **Analysis Requests** - POST to `/run-agent` endpoint
- **Status Polling** - GET from `/results/{job_id}` every 10 seconds
- **File Downloads** - Direct download links from backend endpoints

### State Management
- **React Hooks** - useState and useEffect for local state
- **Job Tracking** - Stores current job ID and status
- **Real-time Updates** - Polling mechanism for live updates

## 📱 User Experience

### Analysis Flow
1. **Input** - User enters research query and API key
2. **Submission** - Frontend starts backend analysis job
3. **Progress** - Real-time updates show agent progress
4. **Results** - Display analysis with citations and downloads
5. **Export** - Multiple download options available

### Agent Status Indicators
- 🟡 **Running** - Agent currently active
- 🟢 **Completed** - Agent finished successfully  
- 🔴 **Failed** - Agent encountered an error
- ⚪ **Pending** - Agent waiting to start

## 🚀 Deployment

### Development
```bash
npm start
```

### Production Build
```bash
npm run build
```

### Static Hosting
The build output can be deployed to:
- **Netlify** - Connect to GitHub for automatic deploys
- **Vercel** - Zero-config deployment
- **AWS S3 + CloudFront** - Scalable static hosting
- **GitHub Pages** - Free hosting for open source

### Environment Configuration
Set `REACT_APP_API_URL` to your backend URL:
- Development: `http://localhost:8000`
- Production: `https://your-api-domain.com`

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch
```

## 📦 Dependencies

### Core Dependencies
- **react** - UI library
- **lucide-react** - Icon components
- **@testing-library** - Testing utilities

### Development Dependencies
- **tailwindcss** - Utility-first CSS framework
- **postcss** - CSS processing
- **autoprefixer** - CSS vendor prefixes

### Build Tools
- **react-scripts** - Create React App build tools
- **web-vitals** - Performance monitoring

## 🎯 Future Enhancements

### Planned Features
- **Analysis History** - View past research jobs
- **User Accounts** - Save and organize research
- **Report Templates** - Customizable output formats
- **Collaboration** - Share and comment on analyses
- **Advanced Filters** - Filter and search results

### Component Improvements
- **Component Library** - Reusable UI components
- **State Management** - Redux or Context for complex state
- **Routing** - Multi-page application with React Router
- **PWA Features** - Offline support and mobile app experience

## 🐛 Troubleshooting

### Common Issues

**API Connection Errors**
- Ensure backend is running on correct port
- Check REACT_APP_API_URL environment variable
- Verify CORS settings in backend

**Build Failures**
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version compatibility
- Verify all dependencies are properly installed

**Styling Issues**
- Ensure Tailwind CSS is properly configured
- Check postcss.config.js and tailwind.config.js
- Verify CSS imports in index.css

## 📊 Performance

### Optimization
- **Code Splitting** - Lazy loading for large components
- **Image Optimization** - Compressed assets
- **Bundle Analysis** - Regular bundle size monitoring
- **Caching** - Browser and CDN caching strategies

### Metrics
- **Core Web Vitals** - LCP, FID, CLS monitoring
- **Load Time** - Initial page load performance
- **Bundle Size** - JavaScript bundle optimization
