import os
from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
import requests
import re
import time
import urllib.parse
import random
from datetime import datetime, timedelta
app = Flask(__name__)

class JobSearcher:
    def __init__(self):
        self.headers = [
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            },
            {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }
        ]
        
    def search_jobs(self, query, location, start=0, num_results=10):
        """Search for jobs using multiple sources"""
        all_jobs = []
        
        # Ensure minimum 10 results
        num_results = max(10, num_results)
        
        # Calculate how many to fetch from each source (at least 5 from each)
        results_per_source = max(5, (num_results + 2) // 3)
        
        # Try Indeed first
        indeed_jobs = self._search_indeed(query, location, results_per_source, start)
        all_jobs.extend(indeed_jobs)
        
        # Try TimesJobs
        timesjobs_jobs = self._search_timesjobs(query, location, results_per_source, start)
        all_jobs.extend(timesjobs_jobs)
        
        # Try Naukri
        naukri_jobs = self._search_naukri(query, location, results_per_source, start)
        all_jobs.extend(naukri_jobs)
        
        if not all_jobs and start == 0:
            return {'error': 'No jobs found. Please try different search terms or check your internet connection.'}
        
        # Filter jobs to match query better
        filtered_jobs = self._filter_relevant_jobs(all_jobs, query)
        
        # Remove duplicates
        unique_jobs = self._remove_duplicates(filtered_jobs)
        
        # Calculate if there are more results
        # We assume there are more if we got at least the requested number
        has_more = len(unique_jobs) >= num_results
        
        # Return the requested number of results
        return_jobs = unique_jobs[:num_results]
        
        return {
            'jobs': return_jobs, 
            'total': len(return_jobs),
            'has_more': has_more,
            'page': (start // num_results) + 1
        }
    
    def _filter_relevant_jobs(self, jobs, query):
        """Filter jobs to match the search query better"""
        query_words = [word.lower() for word in query.split()]
        relevant_jobs = []
        
        for job in jobs:
            title = job.get('title', '').lower()
            description = job.get('description', '').lower()
            company = job.get('company', '').lower()
            
            # Check if any query word appears in title, description, or company
            relevance_score = 0
            for word in query_words:
                if word in title:
                    relevance_score += 3  # Higher weight for title match
                elif word in description:
                    relevance_score += 1
                elif word in company:
                    relevance_score += 2
            
            if relevance_score > 0:
                job['relevance_score'] = relevance_score
                relevant_jobs.append(job)
        
        # Sort by relevance score (highest first)
        relevant_jobs.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return relevant_jobs
    
    def _search_indeed(self, query, location, num_results=5, start=0):
        """Search jobs on Indeed"""
        jobs = []
        try:
            headers = random.choice(self.headers)
            encoded_query = urllib.parse.quote(query)
            encoded_location = urllib.parse.quote(location)
            url = f"https://in.indeed.com/jobs?q={encoded_query}&l={encoded_location}&sort=date&start={start}"
            
            print(f"Searching Indeed: {url} (start={start})")
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try multiple selectors for Indeed job cards
                job_cards = soup.find_all('div', {'data-jk': True}) or \
                           soup.find_all('a', {'data-jk': True}) or \
                           soup.find_all('div', class_=re.compile(r'job_seen_beacon|jobsearch-SerpJobCard|slider_container'))
                
                print(f"Found {len(job_cards)} job cards on Indeed")
                
                for card in job_cards[:num_results * 2]:  # Get more to filter later
                    try:
                        job = self._extract_indeed_job(card)
                        if job and self._is_valid_job(job):
                            jobs.append(job)
                    except Exception as e:
                        print(f"Error extracting Indeed job: {e}")
                        continue
                        
            print(f"Successfully extracted {len(jobs)} jobs from Indeed")
        except Exception as e:
            print(f"Error searching Indeed: {e}")
        
        return jobs[:num_results]
    
    def _search_timesjobs(self, query, location, num_results=5, start=0):
        """Search jobs on TimesJobs"""
        jobs = []
        try:
            headers = random.choice(self.headers)
            encoded_query = urllib.parse.quote(query)
            encoded_location = urllib.parse.quote(location)
            page = (start // 10) + 1
            url = f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords={encoded_query}&txtLocation={encoded_location}&cboWorkExp1=0&cboWorkExp2=30&sequence={page}"
            
            print(f"Searching TimesJobs: {url} (page={page})")
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = soup.find_all('li', class_=re.compile(r'clearfix job-bx')) or \
                           soup.find_all('div', class_=re.compile(r'srp-tuple'))
                
                print(f"Found {len(job_cards)} job cards on TimesJobs")
                
                for card in job_cards[:num_results * 2]:
                    try:
                        job = self._extract_timesjobs_job(card)
                        if job and self._is_valid_job(job):
                            jobs.append(job)
                    except Exception as e:
                        print(f"Error extracting TimesJobs job: {e}")
                        continue
                        
            print(f"Successfully extracted {len(jobs)} jobs from TimesJobs")
        except Exception as e:
            print(f"Error searching TimesJobs: {e}")
        
        return jobs[:num_results]
    
    def _search_naukri(self, query, location, num_results=5, start=0):
        """Search jobs on Naukri"""
        jobs = []
        try:
            headers = random.choice(self.headers)
            encoded_query = urllib.parse.quote(query.replace(' ', '-'))
            encoded_location = urllib.parse.quote(location.replace(' ', '-'))
            page_param = f"-{start}" if start > 0 else ""
            url = f"https://www.naukri.com/{encoded_query}-jobs-in-{encoded_location}{page_param}"
            
            print(f"Searching Naukri: {url} (start={start})")
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = soup.find_all('div', class_=re.compile(r'jobTuple|srp-tuple')) or \
                           soup.find_all('article', class_=re.compile(r'jobTuple'))
                
                print(f"Found {len(job_cards)} job cards on Naukri")
                
                for card in job_cards[:num_results * 2]:
                    try:
                        job = self._extract_naukri_job(card)
                        if job and self._is_valid_job(job):
                            jobs.append(job)
                    except Exception as e:
                        print(f"Error extracting Naukri job: {e}")
                        continue
                        
            print(f"Successfully extracted {len(jobs)} jobs from Naukri")
        except Exception as e:
            print(f"Error searching Naukri: {e}")
        
        return jobs[:num_results]
    
    def _is_valid_job(self, job):
        """Check if job has minimum required information"""
        return (job.get('title', 'Not specified') != 'Not specified' and 
                job.get('company', 'Not specified') != 'Not specified' and
                len(job.get('title', '')) > 3)
    
    def _extract_indeed_job(self, card):
        """Extract job details from Indeed job card"""
        try:
            # Extract title with multiple selectors
            title = self._extract_text(card, [
                'h2[data-testid="job-title"] a',
                'h2 a[data-testid="job-title"]',
                '.jobTitle a',
                'h2 a',
                '[data-testid="job-title"]'
            ])
            
            # Extract company
            company = self._extract_text(card, [
                '[data-testid="company-name"]',
                '.companyName',
                'span[title]',
                'a[data-testid="company-name"]'
            ])
            
            # Extract location
            location = self._extract_text(card, [
                '[data-testid="job-location"]',
                '.companyLocation',
                '.locationsContainer'
            ])
            
            # Extract description/summary
            description = self._extract_text(card, [
                '.summary',
                '[data-testid="job-snippet"]',
                '.job-snippet'
            ])
            
            # Extract posting date
            posted_date = self._extract_date(card, [
                '[data-testid="job-age"]',
                '.date',
                'span[title*="Posted"]',
                'span[title*="ago"]'
            ])
            
            # Extract employment type
            job_type = self._extract_text(card, [
                '[data-testid="job-type-label"]',
                '.jobMetadata',
                '.metadata'
            ]) or 'Full-time'
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'salary': self._extract_salary_from_text(card.get_text()),
                'type': job_type,
                'posted': posted_date,
                'description': self._clean_description(description),
                'links': {'website': 'https://indeed.com'},
                'source': 'Indeed',
                'experience': self._extract_experience(card.get_text()),
                'skills': self._extract_skills(card.get_text())
            }
        except Exception as e:
            print(f"Error in _extract_indeed_job: {e}")
            return None
    
    def _extract_timesjobs_job(self, card):
        """Extract job details from TimesJobs job card"""
        try:
            title = self._extract_text(card, [
                'h2 a',
                '.joblist-jobname',
                '.job-title a',
                'h3 a'
            ])
            
            company = self._extract_text(card, [
                '.joblist-comp-name',
                '.company-name',
                '.comp-name'
            ])
            
            location = self._extract_text(card, [
                '.job-location',
                '.location',
                '.joblist-location'
            ])
            
            description = self._extract_text(card, [
                '.list-job-dtl',
                '.job-description',
                '.joblist-descriptn'
            ])
            
            posted_date = self._extract_date(card, [
                '.job-posted',
                '.posted-date',
                '.joblist-postdate'
            ])
            
            experience = self._extract_text(card, [
                '.joblist-exp',
                '.experience',
                '.exp'
            ])
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'salary': self._extract_salary_from_text(card.get_text()),
                'type': 'Full-time',
                'posted': posted_date,
                'description': self._clean_description(description),
                'links': {'website': 'https://timesjobs.com'},
                'source': 'TimesJobs',
                'experience': experience,
                'skills': self._extract_skills(card.get_text())
            }
        except Exception as e:
            print(f"Error in _extract_timesjobs_job: {e}")
            return None
    
    def _extract_naukri_job(self, card):
        """Extract job details from Naukri job card"""
        try:
            title = self._extract_text(card, [
                '.title',
                '.jobTitle',
                'h3 a',
                '.job-title'
            ])
            
            company = self._extract_text(card, [
                '.subTitle',
                '.companyName',
                '.comp-name'
            ])
            
            location = self._extract_text(card, [
                '.location',
                '.jobLoc',
                '.job-location'
            ])
            
            description = self._extract_text(card, [
                '.job-description',
                '.jobDesc',
                '.job-summary'
            ])
            
            posted_date = self._extract_date(card, [
                '.job-post-day',
                '.postdate',
                '.posted-date'
            ])
            
            experience = self._extract_text(card, [
                '.experience',
                '.exp-text',
                '.jobExp'
            ])
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'salary': self._extract_salary_from_text(card.get_text()),
                'type': 'Full-time',
                'posted': posted_date,
                'description': self._clean_description(description),
                'links': {'website': 'https://naukri.com'},
                'source': 'Naukri',
                'experience': experience,
                'skills': self._extract_skills(card.get_text())
            }
        except Exception as e:
            print(f"Error in _extract_naukri_job: {e}")
            return None
    
    def _extract_text(self, element, selectors):
        """Helper method to extract text from an element using multiple selectors"""
        for selector in selectors:
            try:
                found = element.select_one(selector)
                if found and found.get_text().strip():
                    return found.get_text().strip()
            except:
                continue
        return 'Not specified'
    
    def _extract_date(self, element, selectors):
        """Extract and normalize posting date"""
        for selector in selectors:
            try:
                found = element.select_one(selector)
                if found and found.get_text().strip():
                    date_text = found.get_text().strip().lower()
                    return self._normalize_date(date_text)
            except:
                continue
        
        # Try to find date patterns in the full text
        full_text = element.get_text().lower()
        date_patterns = [
            r'(\d+)\s*day[s]?\s*ago',
            r'(\d+)\s*hour[s]?\s*ago',
            r'posted\s*(\d+)\s*day[s]?\s*ago',
            r'(\d+)\s*week[s]?\s*ago',
            r'today',
            r'yesterday',
            r'just now'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, full_text)
            if match:
                return self._normalize_date(match.group(0))
        
        return 'Recently posted'
    
    def _normalize_date(self, date_text):
        """Convert relative date to readable format"""
        date_text = date_text.lower().strip()
        
        if 'just now' in date_text or 'few minutes' in date_text:
            return 'Just posted'
        elif 'today' in date_text:
            return 'Posted today'
        elif 'yesterday' in date_text:
            return 'Posted yesterday'
        elif 'hour' in date_text:
            hours = re.search(r'(\d+)', date_text)
            if hours:
                h = int(hours.group(1))
                return f'Posted {h} hour{"s" if h > 1 else ""} ago'
        elif 'day' in date_text:
            days = re.search(r'(\d+)', date_text)
            if days:
                d = int(days.group(1))
                if d == 1:
                    return 'Posted 1 day ago'
                elif d <= 7:
                    return f'Posted {d} days ago'
                else:
                    return f'Posted {d} days ago'
        elif 'week' in date_text:
            weeks = re.search(r'(\d+)', date_text)
            if weeks:
                w = int(weeks.group(1))
                return f'Posted {w} week{"s" if w > 1 else ""} ago'
        elif 'month' in date_text:
            months = re.search(r'(\d+)', date_text)
            if months:
                m = int(months.group(1))
                return f'Posted {m} month{"s" if m > 1 else ""} ago'
        
        return 'Recently posted'
    
    def _extract_experience(self, text):
        """Extract experience requirements from text"""
        exp_patterns = [
            r'(\d+)\s*-\s*(\d+)\s*year[s]?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*year[s]?\s*(?:of\s*)?experience',
            r'(\d+)\s*to\s*(\d+)\s*year[s]?',
            r'fresher[s]?',
            r'entry\s*level',
            r'junior',
            r'senior'
        ]
        
        text_lower = text.lower()
        for pattern in exp_patterns:
            match = re.search(pattern, text_lower)
            if match:
                if 'fresher' in match.group(0) or 'entry' in match.group(0):
                    return 'Fresher'
                elif 'junior' in match.group(0):
                    return 'Junior Level'
                elif 'senior' in match.group(0):
                    return 'Senior Level'
                else:
                    return match.group(0).title()
        
        return 'Not specified'
    
    def _extract_skills(self, text):
        """Extract relevant skills from job text"""
        common_skills = [
            'php', 'python', 'java', 'javascript', 'react', 'angular', 'node.js', 'mysql', 
            'mongodb', 'html', 'css', 'bootstrap', 'laravel', 'django', 'spring', 'jquery',
            'git', 'docker', 'kubernetes', 'aws', 'azure', 'linux', 'sql', 'nosql'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in common_skills:
            if skill in text_lower:
                found_skills.append(skill.upper())
        
        return found_skills[:5]  # Return max 5 skills
    
    def _extract_salary_from_text(self, text):
        """Extract salary information from text"""
        try:
            salary_patterns = [
                r'₹\s*(\d+(?:,\d+)*)\s*-\s*₹\s*(\d+(?:,\d+)*)\s*(?:LPA|per annum|PA)',
                r'(\d+)\s*-\s*(\d+)\s*LPA',
                r'₹\s*(\d+(?:,\d+)*)\s*(?:LPA|per annum|PA)',
                r'(\d+)\s*LPA',
                r'\$\s*(\d+(?:,\d+)*)\s*-\s*\$\s*(\d+(?:,\d+)*)\s*(?:per year|annually|k)',
                r'\$\s*(\d+(?:,\d+)*)\s*(?:per year|annually|k)',
                r'(\d+(?:,\d+)*)\s*-\s*(\d+(?:,\d+)*)\s*(?:USD|EUR|GBP)',
                r'(\d+)k\s*-\s*(\d+)k'
            ]
            
            for pattern in salary_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(0)
            
            return 'Not disclosed'
        except:
            return 'Not disclosed'
    
    def _clean_description(self, description):
        """Clean and summarize job description"""
        try:
            if not description or description == 'Not specified':
                return 'No description available'
            
            # Remove extra whitespace and clean text
            text = re.sub(r'\s+', ' ', description).strip()
            
            if len(text) < 100:
                return text
            
            # Take first 3 sentences or first 200 characters
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            summary = ' '.join(sentences[:3])
            
            return summary[:200] + '...' if len(summary) > 200 else summary
        except:
            return 'No description available'
    
    def _remove_duplicates(self, jobs):
        """Remove duplicate jobs based on title and company"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            key = f"{job.get('title', '').lower()}_{job.get('company', '').lower()}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs

@app.route('/')
def index():
    return render_template('dashboard.html', current_year=datetime.now().year)

@app.route('/about')
def about():
    return render_template('about.html', current_year=datetime.now().year)

@app.route('/tech-stack')
def tech_stack():
    return render_template('tech_stack.html', current_year=datetime.now().year)

@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request format'})
            
        query = data.get('query', '').strip()
        location = data.get('location', '').strip()
        start = data.get('start', 0)
        num_results = data.get('num_results', 10)
        
        # Ensure minimum 10 results
        num_results = max(10, num_results)
        
        if not query:
            return jsonify({'error': 'Please enter a job title or keywords'})
        if not location:
            return jsonify({'error': 'Please enter a location'})
        
        if len(query) < 2:
            return jsonify({'error': 'Job title/keywords should be at least 2 characters long'})
        if len(location) < 2:
            return jsonify({'error': 'Location should be at least 2 characters long'})
        
        searcher = JobSearcher()
        results = searcher.search_jobs(query, location, start, num_results)
        
        # Log the results for debugging
        print(f"Search results: {len(results.get('jobs', []))} jobs found, has_more: {results.get('has_more', False)}")
        
        return jsonify(results)
        
    except Exception as e:
        print(f"Error in search route: {e}")
        return jsonify({'error': 'An unexpected error occurred. Please try again.'})

if __name__ == '__main__':
    app.run(debug=True)