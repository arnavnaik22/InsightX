from django.core.management.base import BaseCommand
from analyzer.models import JobRole

JOB_ROLES = [
    {
        "title": "Python / Django Backend Developer",
        "description": "Full-stack Python developer with Django experience",
        "default_jd_text": (
            "We are looking for a skilled Python Backend Developer with strong experience in Django and Django REST Framework. "
            "You will design and implement scalable APIs, work with PostgreSQL and Redis, and deploy applications using Docker and Kubernetes. "
            "Experience with Celery for async task queues, CI/CD pipelines (GitHub Actions / Jenkins), and AWS or GCP cloud services is essential. "
            "Strong knowledge of Python 3.x, REST API design, ORM, unit testing with pytest, and Git version control is required."
        ),
    },
    {
        "title": "Data Scientist / ML Engineer",
        "description": "Machine learning and data science specialist",
        "default_jd_text": (
            "We are hiring a Data Scientist with hands-on experience in machine learning, deep learning, and statistical analysis. "
            "Proficiency in Python (scikit-learn, TensorFlow, PyTorch), SQL, and data visualization tools like Matplotlib and Seaborn is required. "
            "Experience with NLP, feature engineering, model evaluation, A/B testing, and deploying ML models to production using MLflow or SageMaker is expected. "
            "Familiarity with cloud platforms (AWS, GCP, Azure) and big data tools like Spark or Hadoop is a plus."
        ),
    },
    {
        "title": "Frontend Developer (React / Next.js)",
        "description": "Modern frontend developer with React ecosystem expertise",
        "default_jd_text": (
            "We need a talented Frontend Developer proficient in React.js, Next.js, TypeScript, and modern CSS frameworks like Tailwind CSS. "
            "You will build responsive, accessible, and performant web applications, integrate REST APIs and GraphQL, and implement state management using Redux or Zustand. "
            "Experience with testing (Jest, Cypress), build tools (Webpack, Vite), and CI/CD deployment to Vercel or Netlify is preferred. "
            "Strong understanding of web performance optimization, SEO, and browser developer tools is required."
        ),
    },
    {
        "title": "DevOps / Cloud Infrastructure Engineer",
        "description": "DevOps engineer with cloud and infrastructure expertise",
        "default_jd_text": (
            "We are looking for a DevOps Engineer with expertise in cloud infrastructure, CI/CD, and containerization. "
            "Proficiency in AWS (EC2, S3, RDS, Lambda), Docker, Kubernetes, Terraform, and Ansible is required. "
            "You will manage CI/CD pipelines using GitHub Actions, Jenkins, or GitLab CI, monitor systems with Prometheus and Grafana, "
            "and implement infrastructure-as-code best practices. Experience in Linux administration, networking, and security hardening is essential."
        ),
    },
    {
        "title": "Full Stack Developer (MERN / MEAN)",
        "description": "Full stack JavaScript developer",
        "default_jd_text": (
            "We are seeking a Full Stack JavaScript Developer experienced in the MERN stack (MongoDB, Express.js, React, Node.js). "
            "You will develop end-to-end web applications, design REST APIs, manage NoSQL databases, and integrate third-party services. "
            "Experience with authentication (JWT, OAuth2), real-time features (WebSocket, Socket.IO), TypeScript, and cloud deployment (AWS, Heroku) is required. "
            "Knowledge of testing frameworks (Mocha, Jest), Git workflows, and Agile methodologies is expected."
        ),
    },
    {
        "title": "Android / Mobile Developer",
        "description": "Native Android or cross-platform mobile developer",
        "default_jd_text": (
            "We are looking for a Mobile Developer with strong experience in Android development using Kotlin or Java, or cross-platform frameworks like Flutter or React Native. "
            "You will design and publish mobile applications to the Google Play Store, integrate REST APIs and Firebase services, and implement MVVM architecture. "
            "Experience with Jetpack Compose, Room database, Retrofit, Coroutines, and Google Maps SDK is required. "
            "Knowledge of app performance optimization, unit testing, and CI/CD for mobile apps is a plus."
        ),
    },
    {
        "title": "Cybersecurity / Information Security Analyst",
        "description": "Security analyst with threat detection and compliance skills",
        "default_jd_text": (
            "We need an Information Security Analyst to protect our systems and data from cyber threats. "
            "You will conduct vulnerability assessments, penetration testing, SIEM monitoring, and incident response. "
            "Expertise in network security, firewalls, IDS/IPS, OWASP Top 10, and compliance frameworks (ISO 27001, SOC 2, GDPR) is required. "
            "Proficiency in tools like Metasploit, Burp Suite, Nessus, Wireshark, and scripting (Python, Bash) for automation is expected. "
            "Relevant certifications such as CEH, CISSP, or CompTIA Security+ are a strong advantage."
        ),
    },
    {
        "title": "UI/UX Designer",
        "description": "User experience and interface design professional",
        "default_jd_text": (
            "We are hiring a UI/UX Designer to create intuitive and visually compelling digital experiences. "
            "You will conduct user research, usability testing, wireframing, and high-fidelity prototyping using Figma or Adobe XD. "
            "Strong understanding of design systems, accessibility (WCAG), user psychology, and responsive design principles is required. "
            "Experience collaborating with frontend developers, translating designs to CSS/HTML, and iterating based on user feedback is expected."
        ),
    },
]


class Command(BaseCommand):
    help = "Seeds the database with predefined job role templates"

    def handle(self, *args, **options):
        created = 0
        skipped = 0
        for role_data in JOB_ROLES:
            _, was_created = JobRole.objects.get_or_create(
                title=role_data["title"],
                defaults={
                    "description": role_data["description"],
                    "default_jd_text": role_data["default_jd_text"],
                },
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"  Created: {role_data['title']}"))
            else:
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(f"\nDone! Created {created} job roles, skipped {skipped} already existing.")
        )
