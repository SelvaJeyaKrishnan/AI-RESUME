"""
A curated skills taxonomy used to detect skills mentioned in resumes and job
descriptions via phrase matching. This is intentionally a plain Python data
structure (not a DB table) so it ships with the app and needs no seeding step;
matched skill names are still persisted to the Skill/CandidateSkill tables.

Keys are canonical skill names; values are alternate surface forms (aliases)
that should also match. Matching is case-insensitive and word-boundary aware.
"""

SKILLS_TAXONOMY: dict[str, list[str]] = {
    # Programming languages
    "Python": ["python", "python3"],
    "JavaScript": ["javascript", "js", "es6"],
    "TypeScript": ["typescript", "ts"],
    "Java": ["java"],
    "C++": ["c++", "cpp"],
    "C#": ["c#", "csharp", ".net"],
    "Go": ["golang", " go "],
    "Rust": ["rust"],
    "Ruby": ["ruby"],
    "PHP": ["php"],
    "Swift": ["swift"],
    "Kotlin": ["kotlin"],
    "R": ["r programming", " r "],
    "SQL": ["sql"],
    "Scala": ["scala"],

    # Web / frontend
    "React": ["react", "react.js", "reactjs"],
    "Vue.js": ["vue", "vue.js", "vuejs"],
    "Angular": ["angular", "angularjs"],
    "Next.js": ["next.js", "nextjs"],
    "HTML/CSS": ["html", "css", "html5", "css3"],
    "Tailwind CSS": ["tailwind", "tailwindcss"],
    "Redux": ["redux"],

    # Backend / frameworks
    "FastAPI": ["fastapi"],
    "Django": ["django"],
    "Flask": ["flask"],
    "Node.js": ["node.js", "nodejs", "node"],
    "Express.js": ["express.js", "expressjs", "express"],
    "Spring Boot": ["spring boot", "spring"],
    ".NET Core": [".net core", "dotnet core"],
    "GraphQL": ["graphql"],
    "REST API": ["rest api", "restful", "rest apis"],

    # Data / ML / AI
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning", "dl"],
    "Natural Language Processing": ["nlp", "natural language processing"],
    "Computer Vision": ["computer vision", "cv"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Data Analysis": ["data analysis", "data analytics"],
    "Data Visualization": ["data visualization", "tableau", "power bi"],
    "Big Data": ["big data", "spark", "apache spark", "hadoop"],
    "LLM": ["llm", "large language model", "generative ai", "genai"],

    # Databases
    "PostgreSQL": ["postgresql", "postgres"],
    "MySQL": ["mysql"],
    "MongoDB": ["mongodb", "mongo"],
    "Redis": ["redis"],
    "SQLite": ["sqlite"],
    "Elasticsearch": ["elasticsearch", "elastic search"],

    # Cloud / DevOps
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure", "microsoft azure"],
    "Google Cloud": ["gcp", "google cloud"],
    "Docker": ["docker", "containerization"],
    "Kubernetes": ["kubernetes", "k8s"],
    "CI/CD": ["ci/cd", "continuous integration", "continuous deployment"],
    "Terraform": ["terraform"],
    "Jenkins": ["jenkins"],
    "Git": ["git", "github", "gitlab", "version control"],
    "Linux": ["linux", "unix"],

    # Mobile
    "iOS Development": ["ios development", "ios"],
    "Android Development": ["android development", "android"],
    "React Native": ["react native"],
    "Flutter": ["flutter"],

    # Soft / general skills
    "Project Management": ["project management", "pmp"],
    "Agile/Scrum": ["agile", "scrum", "kanban"],
    "Communication": ["communication skills", "communication"],
    "Leadership": ["leadership", "team lead", "people management"],
    "Problem Solving": ["problem solving", "problem-solving"],
    "System Design": ["system design", "distributed systems"],

    # Design
    "UI/UX Design": ["ui/ux", "ux design", "ui design", "figma"],

    # Testing
    "Unit Testing": ["unit testing", "pytest", "jest", "test-driven development", "tdd"],

    # Business / other
    "Product Management": ["product management"],
    "Digital Marketing": ["digital marketing", "seo", "sem"],
    "Sales": ["b2b sales", "sales strategy"],
    "Excel": ["excel", "microsoft excel"],
}


def get_all_skill_names() -> list[str]:
    return list(SKILLS_TAXONOMY.keys())
