# JobScout - Intelligent Job Search Platform

A modern web application that intelligently aggregates and filters job listings from multiple Indian job portals, helping you find the perfect opportunity faster and more efficiently.

![JobScout](https://img.shields.io/badge/JobScout-v1.0-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Flask](https://img.shields.io/badge/Flask-2.0+-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Key Features

- 🔍 **Unified Search**: One search, multiple portals (Indeed, TimesJobs, Naukri)
- ⚡ **Real-time Updates**: Fresh job listings as they're posted
- 🎯 **Smart Filtering**: AI-powered relevance scoring and filtering
- 📱 **Mobile-First**: Seamless experience across all devices
- 💼 **Job Tracking**: Save and organize interesting opportunities
- 📊 **Insights**: Salary trends and market analysis
- 🔔 **Alerts**: Get notified about new matching jobs
- 📈 **Career Analytics**: Track your job search progress

## 🛠️ Technology Stack

### Backend
- Python 3.8+
- Flask (Web Framework)
- BeautifulSoup4 (Web Scraping)
- Redis (Caching)
- SQLite (Data Storage)

### Frontend
- HTML5 & CSS3
- Bootstrap 5
- JavaScript (ES6+)
- Font Awesome Icons

## 🚀 Getting Started

1. Clone the repository:
```bash
git clone https://github.com/vedanshvijay/jobscout.git
cd jobscout
```

2. Set up virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Visit `http://localhost:5000` in your browser (or `http://localhost:5001` if port 5000 is in use)

## 📁 Project Structure

```
jobscout/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── .gitignore         # Git ignore rules
├── README.md          # Project documentation
└── templates/         # HTML templates
    ├── base.html     # Base template
    ├── dashboard.html # Main interface
    ├── about.html    # About page
    └── tech_stack.html # Tech stack page
```

## 💡 Features in Detail

### Smart Search
- Multi-portal aggregation
- Intelligent keyword matching
- Location-based filtering
- Experience level filtering
- Salary range filtering

### Job Management
- Save interesting jobs
- Track application status
- Set up job alerts
- Export job listings
- Share opportunities

### Analytics
- Job market trends
- Salary insights
- Skill demand analysis
- Application success rate
- Search history

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Developer

**Vedansh Vijayvargia**
- GitHub: [@vedanshvijay](https://github.com/vedanshvijay)
- LinkedIn: [Vedansh Vijayvargia](https://www.linkedin.com/in/vedansh-vijayvargia-41a64421b)
- Email: ved02vijay@gmail.com

## 🙏 Acknowledgments

- Thanks to all job portals for providing public job listings
- Inspired by the need for better job search tools in India
- Built with modern web technologies for optimal performance

## 📊 Demo

Visit the live demo: [JobScout Live](https://your-demo-url.com) *(Update with your deployment URL)*

---

⭐ **Star this repository if you find it helpful!** 