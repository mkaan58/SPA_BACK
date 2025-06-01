BASE_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modern Website - Base Template</title>
    <meta name="description" content="Modern responsive website with dark/light theme toggle">
    <meta name="keywords" content="portfolio, modern, responsive, professional">
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    
    <!-- AOS CSS -->
    <link href="https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.css" rel="stylesheet">
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/@emailjs/browser@4/dist/email.min.js"></script>
    <script>
        emailjs.init("{{ YOUR_EMAIL_JS_PUBLIC_KEY }}");
    </script>
    
    <!-- Custom Styles -->
    <style>
        :root {
            --primary-color: #4F46E5;
            --secondary-color: #7C3AED;
            --accent-color: #F59E0B;
            --bg-light: #FFFFFF;
            --bg-dark: #111827;
            --text-light: #111827;
            --text-dark: #F9FAFB;
        }
        
        * {
            transition: all 0.3s ease;
        }
        
        .dark {
            --tw-bg-opacity: 1;
            background-color: rgb(17 24 39 / var(--tw-bg-opacity));
            color: rgb(249 250 251 / var(--tw-bg-opacity));
        }
        
        .font-heading {
            font-family: 'Playfair Display', serif;
        }
        
        .font-body {
            font-family: 'Inter', sans-serif;
        }
        
        .smooth-scroll {
            scroll-behavior: smooth;
            scroll-padding-top: 80px;
        }
        
        .gradient-bg {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        }
        
        .glass-effect {
            backdrop-filter: blur(10px);
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .dark .glass-effect {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .hover-lift:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(79, 70, 229, 0.3);
        }
        
        .mobile-menu {
            transform: translateX(100%);
            transition: transform 0.3s ease;
        }
        
        .mobile-menu.active {
            transform: translateX(0);
        }
        
        .hamburger span {
            display: block;
            width: 25px;
            height: 3px;
            background: currentColor;
            transition: all 0.3s ease;
            transform-origin: center;
        }
        
        .hamburger.active span:nth-child(1) {
            transform: rotate(45deg) translate(6px, 6px);
        }
        
        .hamburger.active span:nth-child(2) {
            opacity: 0;
        }
        
        .hamburger.active span:nth-child(3) {
            transform: rotate(-45deg) translate(6px, -6px);
        }
    </style>
</head>
<body class="font-body smooth-scroll bg-white dark:bg-gray-900 text-gray-900 dark:text-white" x-data="{ 
    mobileMenuOpen: false, 
    darkMode: localStorage.getItem('darkMode') === 'true' || (!localStorage.getItem('darkMode') && window.matchMedia('(prefers-color-scheme: dark)').matches),
    showBackToTop: false,
    activeSection: 'home'
}" x-init="
    if (darkMode) document.documentElement.classList.add('dark');
    $watch('darkMode', value => {
        if (value) {
            document.documentElement.classList.add('dark');
            localStorage.setItem('darkMode', 'true');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('darkMode', 'false');
        }
    });
    
    window.addEventListener('scroll', () => {
        showBackToTop = window.scrollY > 300;
    });
">

    <!-- Navigation -->
    <nav class="fixed top-0 left-0 right-0 z-50 bg-white/90 dark:bg-gray-900/90 backdrop-blur-md border-b border-gray-200 dark:border-gray-700">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <!-- Logo -->
                <div class="flex-shrink-0">
                    <a href="#home" class="font-heading text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                        Your Brand
                    </a>
                </div>
                
                <!-- Desktop Navigation -->
                <div class="hidden md:block">
                    <div class="ml-10 flex items-baseline space-x-8">
                        <a href="#home" class="nav-link text-gray-900 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400 px-3 py-2 text-sm font-medium transition-colors">Home</a>
                        <a href="#about" class="nav-link text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 px-3 py-2 text-sm font-medium transition-colors">About</a>
                        <a href="#portfolio" class="nav-link text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 px-3 py-2 text-sm font-medium transition-colors">Portfolio</a>
                        <a href="#projects" class="nav-link text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 px-3 py-2 text-sm font-medium transition-colors">Projects</a>
                        <a href="#contact" class="nav-link text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 px-3 py-2 text-sm font-medium transition-colors">Contact</a>
                        
                        <!-- Theme Toggle -->
                        <button @click="darkMode = !darkMode" class="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors" aria-label="Toggle dark mode">
                            <i class="fas fa-sun text-yellow-500" x-show="darkMode"></i>
                            <i class="fas fa-moon text-indigo-600" x-show="!darkMode"></i>
                        </button>
                    </div>
                </div>
                
                <!-- Mobile menu button -->
                <div class="md:hidden flex items-center space-x-2">
                    <!-- Mobile Theme Toggle -->
                    <button @click="darkMode = !darkMode" class="p-2 rounded-lg bg-gray-100 dark:bg-gray-800" aria-label="Toggle dark mode">
                        <i class="fas fa-sun text-yellow-500" x-show="darkMode"></i>
                        <i class="fas fa-moon text-indigo-600" x-show="!darkMode"></i>
                    </button>
                    
                    <button @click="mobileMenuOpen = !mobileMenuOpen" class="hamburger p-2" :class="{ 'active': mobileMenuOpen }" aria-label="Toggle menu">
                        <span></span>
                        <span></span>
                        <span></span>
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Mobile Navigation -->
        <div class="md:hidden fixed top-16 right-0 h-screen w-64 bg-white dark:bg-gray-900 shadow-xl mobile-menu" :class="{ 'active': mobileMenuOpen }">
            <div class="px-2 pt-2 pb-3 space-y-1">
                <a href="#home" @click="mobileMenuOpen = false" class="block px-3 py-2 text-base font-medium text-gray-900 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400">Home</a>
                <a href="#about" @click="mobileMenuOpen = false" class="block px-3 py-2 text-base font-medium text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400">About</a>
                <a href="#portfolio" @click="mobileMenuOpen = false" class="block px-3 py-2 text-base font-medium text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400">Portfolio</a>
                <a href="#projects" @click="mobileMenuOpen = false" class="block px-3 py-2 text-base font-medium text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400">Projects</a>
                <a href="#contact" @click="mobileMenuOpen = false" class="block px-3 py-2 text-base font-medium text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400">Contact</a>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section id="home" class="min-h-screen flex items-center justify-center relative overflow-hidden">
        <div class="absolute inset-0 gradient-bg opacity-10"></div>
        <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <div data-aos="fade-up" data-aos-duration="1000">
                <h1 class="font-heading text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                    Welcome to Modern Design
                </h1>
                <p class="text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
                    Creating innovative digital experiences with cutting-edge technology and stunning visual design.
                </p>
                <div class="flex flex-col sm:flex-row gap-4 justify-center">
                    <a href="#portfolio" class="btn-primary">
                        <i class="fas fa-rocket mr-2"></i>
                        View My Work
                    </a>
                    <a href="#contact" class="px-6 py-3 border-2 border-indigo-600 text-indigo-600 dark:text-indigo-400 rounded-lg font-semibold hover:bg-indigo-600 hover:text-white transition-all">
                        <i class="fas fa-envelope mr-2"></i>
                        Get In Touch
                    </a>
                </div>
            </div>
        </div>
    </section>

    <!-- About Section -->
    <section id="about" class="py-20 bg-gray-50 dark:bg-gray-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center mb-16" data-aos="fade-up">
                <h2 class="font-heading text-3xl md:text-4xl font-bold mb-4">About Me</h2>
                <p class="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
                    Passionate about creating digital experiences that make a difference
                </p>
            </div>
            
            <div class="grid lg:grid-cols-2 gap-12 items-center">
                <div data-aos="fade-right">
                    <img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500&h=600&fit=crop&auto=format" 
                         alt="Profile" 
                         class="rounded-2xl shadow-2xl w-full max-w-md mx-auto hover-lift"
                         loading="lazy">
                </div>
                
                <div data-aos="fade-left">
                    <h3 class="font-heading text-2xl font-bold mb-6">Creative Developer & Designer</h3>
                    <p class="text-gray-600 dark:text-gray-300 mb-6 leading-relaxed">
                        With over 5 years of experience in web development and design, I specialize in creating 
                        modern, responsive websites that not only look stunning but also provide exceptional user experiences.
                    </p>
                    
                    <div class="grid grid-cols-2 gap-4 mb-8">
                        <div class="text-center p-4 bg-white dark:bg-gray-700 rounded-lg shadow-md">
                            <div class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">50+</div>
                            <div class="text-sm text-gray-600 dark:text-gray-300">Projects Completed</div>
                        </div>
                        <div class="text-center p-4 bg-white dark:bg-gray-700 rounded-lg shadow-md">
                            <div class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">5+</div>
                            <div class="text-sm text-gray-600 dark:text-gray-300">Years Experience</div>
                        </div>
                    </div>
                    
                    <div class="flex flex-wrap gap-3">
                        <span class="px-3 py-1 bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300 rounded-full text-sm">JavaScript</span>
                        <span class="px-3 py-1 bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300 rounded-full text-sm">React</span>
                        <span class="px-3 py-1 bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300 rounded-full text-sm">UI/UX Design</span>
                        <span class="px-3 py-1 bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300 rounded-full text-sm">Tailwind CSS</span>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Portfolio Section -->
    <section id="portfolio" class="py-20">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center mb-16" data-aos="fade-up">
                <h2 class="font-heading text-3xl md:text-4xl font-bold mb-4">Portfolio</h2>
                <p class="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
                    A showcase of my latest work and creative projects
                </p>
            </div>
            
            <!-- Portfolio Filter -->
            <div class="text-center mb-12" x-data="{ activeFilter: 'all' }">
                <div class="inline-flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
                    <button @click="activeFilter = 'all'" :class="activeFilter === 'all' ? 'bg-white dark:bg-gray-700 shadow-md' : ''" class="px-4 py-2 rounded-md text-sm font-medium transition-all">All</button>
                    <button @click="activeFilter = 'web'" :class="activeFilter === 'web' ? 'bg-white dark:bg-gray-700 shadow-md' : ''" class="px-4 py-2 rounded-md text-sm font-medium transition-all">Web Design</button>
                    <button @click="activeFilter = 'mobile'" :class="activeFilter === 'mobile' ? 'bg-white dark:bg-gray-700 shadow-md' : ''" class="px-4 py-2 rounded-md text-sm font-medium transition-all">Mobile Apps</button>
                    <button @click="activeFilter = 'branding'" :class="activeFilter === 'branding' ? 'bg-white dark:bg-gray-700 shadow-md' : ''" class="px-4 py-2 rounded-md text-sm font-medium transition-all">Branding</button>
                </div>
            </div>
            
            <!-- Portfolio Grid -->
            <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                <!-- Portfolio Item 1 -->
                <div class="group relative overflow-hidden rounded-2xl shadow-lg hover-lift" data-aos="zoom-in" data-aos-delay="100">
                    <img src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&h=400&fit=crop&auto=format" 
                         alt="E-commerce Platform" 
                         class="w-full h-64 object-cover group-hover:scale-110 transition-transform duration-500"
                         loading="lazy">
                    <div class="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                        <div class="absolute bottom-0 left-0 right-0 p-6 text-white">
                            <h3 class="text-xl font-semibold mb-2">E-commerce Platform</h3>
                            <p class="text-gray-200 text-sm mb-4">Modern online shopping experience with advanced features</p>
                            <div class="flex space-x-2">
                                <button class="p-2 bg-white/20 rounded-full hover:bg-white/30 transition-colors">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="p-2 bg-white/20 rounded-full hover:bg-white/30 transition-colors">
                                    <i class="fas fa-external-link-alt"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Portfolio Item 2 -->
                <div class="group relative overflow-hidden rounded-2xl shadow-lg hover-lift" data-aos="zoom-in" data-aos-delay="200">
                    <img src="https://images.unsplash.com/photo-1551650975-87deedd944c3?w=600&h=400&fit=crop&auto=format" 
                         alt="Mobile App Design" 
                         class="w-full h-64 object-cover group-hover:scale-110 transition-transform duration-500"
                         loading="lazy">
                    <div class="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                        <div class="absolute bottom-0 left-0 right-0 p-6 text-white">
                            <h3 class="text-xl font-semibold mb-2">Mobile App Design</h3>
                            <p class="text-gray-200 text-sm mb-4">Intuitive mobile interface with seamless user experience</p>
                            <div class="flex space-x-2">
                                <button class="p-2 bg-white/20 rounded-full hover:bg-white/30 transition-colors">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="p-2 bg-white/20 rounded-full hover:bg-white/30 transition-colors">
                                    <i class="fas fa-external-link-alt"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Portfolio Item 3 -->
                <div class="group relative overflow-hidden rounded-2xl shadow-lg hover-lift" data-aos="zoom-in" data-aos-delay="300">
                    <img src="https://images.unsplash.com/photo-1558655146-9f40138edfeb?w=600&h=400&fit=crop&auto=format" 
                         alt="Brand Identity" 
                         class="w-full h-64 object-cover group-hover:scale-110 transition-transform duration-500"
                         loading="lazy">
                    <div class="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                        <div class="absolute bottom-0 left-0 right-0 p-6 text-white">
                            <h3 class="text-xl font-semibold mb-2">Brand Identity</h3>
                            <p class="text-gray-200 text-sm mb-4">Complete branding solution with logo and visual system</p>
                            <div class="flex space-x-2">
                                <button class="p-2 bg-white/20 rounded-full hover:bg-white/30 transition-colors">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="p-2 bg-white/20 rounded-full hover:bg-white/30 transition-colors">
                                    <i class="fas fa-external-link-alt"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Portfolio Item 4 -->
                <div class="group relative overflow-hidden rounded-2xl shadow-lg hover-lift" data-aos="zoom-in" data-aos-delay="100">
                    <img src="https://images.unsplash.com/photo-1499951360447-b19be8fe80f5?w=600&h=400&fit=crop&auto=format" 
                         alt="Web Application" 
                         class="w-full h-64 object-cover group-hover:scale-110 transition-transform duration-500"
                         loading="lazy">
                    <div class="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                        <div class="absolute bottom-0 left-0 right-0 p-6 text-white">
                            <h3 class="text-xl font-semibold mb-2">Web Application</h3>
                            <p class="text-gray-200 text-sm mb-4">Full-stack web application with modern architecture</p>
                            <div class="flex space-x-2">
                                <button class="p-2 bg-white/20 rounded-full hover:bg-white/30 transition-colors">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="p-2 bg-white/20 rounded-full hover:bg-white/30 transition-colors">
                                    <i class="fas fa-external-link-alt"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Portfolio Item 5 -->
                <div class="group relative overflow-hidden rounded-2xl shadow-lg hover-lift" data-aos="zoom-in" data-aos-delay="200">
                    <img src="https://images.unsplash.com/photo-1586717791821-3f44a563fa4c?w=600&h=400&fit=crop&auto=format" 
                         alt="Dashboard Design" 
                         class="w-full h-64 object-cover group-hover:scale-110 transition-transform duration-500"
                         loading="lazy">
                    <div class="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                        <div class="absolute bottom-0 left-0 right-0 p-6 text-white">
                            <h3 class="text-xl font-semibold mb-2">Dashboard Design</h3>
                            <p class="text-gray-200 text-sm mb-4">Clean and intuitive admin dashboard interface</p>
                            <div class="flex space-x-2">
                                <button class="p-2 bg-white/20 rounded-full hover:bg-white/30 transition-colors">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="p-2 bg-white/20 rounded-full hover:bg-white/30 transition-colors">
                                    <i class="fas fa-external-link-alt"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Portfolio Item 6 -->
                <div class="group relative overflow-hidden rounded-2xl shadow-lg hover-lift" data-aos="zoom-in" data-aos-delay="300">
                    <img src="https://images.unsplash.com/photo-1557804506-669a67965ba0?w=600&h=400&fit=crop&auto=format" 
                         alt="Website Redesign" 
                         class="w-full h-64 object-cover group-hover:scale-110 transition-transform duration-500"
                         loading="lazy">
                    <div class="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                        <div class="absolute bottom-0 left-0 right-0 p-6 text-white">
                            <h3 class="text-xl font-semibold mb-2">Website Redesign</h3>
                            <p class="text-gray-200 text-sm mb-4">Complete website makeover with improved UX</p>
                            <div class="flex space-x-2">
                                <button class="p-2 bg-white/20 rounded-full hover:bg-white/30 transition-colors">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="p-2 bg-white/20 rounded-full hover:bg-white/30 transition-colors">
                                    <i class="fas fa-external-link-alt"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Projects Section -->
    <section id="projects" class="py-20 bg-gray-50 dark:bg-gray-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center mb-16" data-aos="fade-up">
                <h2 class="font-heading text-3xl md:text-4xl font-bold mb-4">Recent Projects</h2>
                <p class="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
                    Exploring innovative solutions and cutting-edge technologies
                </p>
            </div>
            
            <div class="grid lg:grid-cols-2 gap-12">
                <!-- Project 1 -->
                <div class="bg-white dark:bg-gray-700 rounded-2xl shadow-xl overflow-hidden hover-lift" data-aos="fade-up" data-aos-delay="100">
                    <img src="https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=300&fit=crop&auto=format" 
                         alt="AI-Powered Analytics" 
                         class="w-full h-48 object-cover"
                         loading="lazy">
                    <div class="p-8">
                        <h3 class="font-heading text-2xl font-bold mb-4">AI-Powered Analytics Platform</h3>
                        <p class="text-gray-600 dark:text-gray-300 mb-6">
                            Advanced data visualization and machine learning insights dashboard built with modern web technologies.
                        </p>
                        <div class="flex flex-wrap gap-2 mb-6">
                            <span class="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300 rounded-full text-sm">React</span>
                            <span class="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-600 dark:text-green-300 rounded-full text-sm">Node.js</span>
                            <span class="px-3 py-1 bg-purple-100 dark:bg-purple-900 text-purple-600 dark:text-purple-300 rounded-full text-sm">Python</span>
                            <span class="px-3 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-600 dark:text-yellow-300 rounded-full text-sm">TensorFlow</span>
                        </div>
                        <div class="flex items-center justify-between">
                            <a href="#" class="text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 font-semibold flex items-center">
                                <i class="fas fa-external-link-alt mr-2"></i>
                                View Project
                            </a>
                            <a href="#" class="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                                <i class="fab fa-github text-xl"></i>
                            </a>
                        </div>
                    </div>
                </div>
                
                <!-- Project 2 -->
                <div class="bg-white dark:bg-gray-700 rounded-2xl shadow-xl overflow-hidden hover-lift" data-aos="fade-up" data-aos-delay="200">
                    <img src="https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=600&h=300&fit=crop&auto=format" 
                         alt="E-commerce Mobile App" 
                         class="w-full h-48 object-cover"
                         loading="lazy">
                    <div class="p-8">
                        <h3 class="font-heading text-2xl font-bold mb-4">E-commerce Mobile App</h3>
                        <p class="text-gray-600 dark:text-gray-300 mb-6">
                            Cross-platform mobile application with seamless shopping experience and real-time notifications.
                        </p>
                        <div class="flex flex-wrap gap-2 mb-6">
                            <span class="px-3 py-1 bg-cyan-100 dark:bg-cyan-900 text-cyan-600 dark:text-cyan-300 rounded-full text-sm">React Native</span>
                            <span class="px-3 py-1 bg-orange-100 dark:bg-orange-900 text-orange-600 dark:text-orange-300 rounded-full text-sm">Firebase</span>
                            <span class="px-3 py-1 bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-300 rounded-full text-sm">Stripe</span>
                        </div>
                        <div class="flex items-center justify-between">
                            <a href="#" class="text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 font-semibold flex items-center">
                                <i class="fas fa-external-link-alt mr-2"></i>
                                View Project
                            </a>
                            <a href="#" class="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                                <i class="fab fa-github text-xl"></i>
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

<!-- Contact Section - EmailJS Playground yapısına uygun -->
<section id="contact" class="py-20">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16" data-aos="fade-up">
            <h2 class="font-heading text-3xl md:text-4xl font-bold mb-4">Get In Touch</h2>
            <p class="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
                Let's discuss your next project and bring your ideas to life
            </p>
        </div>
        
        <div class="grid lg:grid-cols-2 gap-12">
            <!-- Contact Info -->
            <div data-aos="fade-right">
                <h3 class="font-heading text-2xl font-bold mb-8">Let's Connect</h3>
                <div class="space-y-6">
                    <div class="flex items-center">
                        <div class="w-12 h-12 bg-indigo-100 dark:bg-indigo-900 rounded-lg flex items-center justify-center mr-4">
                            <i class="fas fa-envelope text-indigo-600 dark:text-indigo-400"></i>
                        </div>
                        <div>
                            <h4 class="font-semibold">Email</h4>
                            <p class="text-gray-600 dark:text-gray-300">hello@example.com</p>
                        </div>
                    </div>
                    <div class="flex items-center">
                        <div class="w-12 h-12 bg-indigo-100 dark:bg-indigo-900 rounded-lg flex items-center justify-center mr-4">
                            <i class="fas fa-phone text-indigo-600 dark:text-indigo-400"></i>
                        </div>
                        <div>
                            <h4 class="font-semibold">Phone</h4>
                            <p class="text-gray-600 dark:text-gray-300">+1 (555) 123-4567</p>
                        </div>
                    </div>
                    <div class="flex items-center">
                        <div class="w-12 h-12 bg-indigo-100 dark:bg-indigo-900 rounded-lg flex items-center justify-center mr-4">
                            <i class="fas fa-map-marker-alt text-indigo-600 dark:text-indigo-400"></i>
                        </div>
                        <div>
                            <h4 class="font-semibold">Location</h4>
                            <p class="text-gray-600 dark:text-gray-300">San Francisco, CA</p>
                        </div>
                    </div>
                </div>
                <!-- Social Media -->
                <div class="mt-8">
                    <h4 class="font-semibold mb-4">Follow Me</h4>
                    <div class="flex space-x-4">
                        <a href="https://twitter.com/username" class="w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center hover:bg-blue-500 hover:text-white transition-all">
                            <i class="fab fa-twitter"></i>
                        </a>
                        <a href="https://linkedin.com/in/username" class="w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center hover:bg-blue-600 hover:text-white transition-all">
                            <i class="fab fa-linkedin-in"></i>
                        </a>
                        <a href="https://github.com/username" class="w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center hover:bg-gray-800 hover:text-white transition-all">
                            <i class="fab fa-github"></i>
                        </a>
                        <a href="https://dribbble.com/username" class="w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center hover:bg-pink-500 hover:text-white transition-all">
                            <i class="fab fa-dribbble"></i>
                        </a>
                    </div>
                </div>
            </div>
            
            <!-- Contact Form - EmailJS Playground Compatible -->
            <div data-aos="fade-left">
                <div class="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-lg">
                    <h3 class="font-heading text-xl font-bold mb-6 text-gray-900 dark:text-white">Send Message</h3>
                    
                    <!-- EXACT EmailJS Form Structure -->
                    <form id="emailjs-form" class="space-y-6">
                        <div class="grid md:grid-cols-2 gap-6">
                            <div class="field">
                                <label for="name" class="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                                    <i class="fas fa-user mr-2"></i>Name
                                </label>
                                <input 
                                    type="text" 
                                    name="name" 
                                    id="name"
                                    required
                                    class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-colors"
                                    placeholder="Your Name">
                            </div>
                            <div class="field">
                                <label for="email" class="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                                    <i class="fas fa-envelope mr-2"></i>Email
                                </label>
                                <input 
                                    type="email" 
                                    name="email" 
                                    id="email"
                                    required
                                    class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-colors"
                                    placeholder="your@email.com">
                            </div>
                        </div>
                        <div class="field">
                            <label for="subject" class="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                                <i class="fas fa-tag mr-2"></i>Subject
                            </label>
                            <input 
                                type="text" 
                                name="subject" 
                                id="subject"
                                required
                                class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-colors"
                                placeholder="Project Inquiry">
                        </div>
                        <div class="field">
                            <label for="message" class="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                                <i class="fas fa-comment mr-2"></i>Message
                            </label>
                            <textarea 
                                name="message" 
                                id="message"
                                required
                                rows="5"
                                class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none transition-colors"
                                placeholder="Tell me about your project..."></textarea>
                        </div>
                        
                        <!-- Hidden field for recipient email - EmailJS playground style -->
                        <div class="field hidden">
                            <input type="hidden" name="to_email" id="to_email" value="USER_EMAIL_PLACEHOLDER">
                        </div>
                        
                        <button 
                            type="submit" 
                            id="contact-btn"
                            class="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-4 px-6 rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
                            <span>
                                <i class="fas fa-paper-plane mr-2"></i>
                                Send Message
                            </span>
                        </button>
                        
                        <!-- Success/Error Messages -->
                        <div id="success-message" class="hidden text-green-600 dark:text-green-400 text-center py-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                            <i class="fas fa-check-circle mr-2"></i>
                            Message sent successfully! I'll get back to you soon.
                        </div>
                        <div id="error-message" class="hidden text-red-600 dark:text-red-400 text-center py-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                            <i class="fas fa-exclamation-circle mr-2"></i>
                            <span id="error-text">Failed to send message. Please try again.</span>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</section>

    <!-- Footer -->
    <footer class="bg-gray-900 dark:bg-black text-white py-12">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="grid md:grid-cols-4 gap-8">
                <!-- Logo & Description -->
                <div class="md:col-span-2">
                    <div class="font-heading text-2xl font-bold mb-4 text-indigo-400">Your Brand</div>
                    <p class="text-gray-300 mb-6 max-w-md">
                        Creating digital experiences that inspire and connect. Let's build something amazing together.
                    </p>
                    <div class="flex space-x-4">
                        <a href="https://twitter.com/username" class="text-gray-400 hover:text-white transition-colors">
                            <i class="fab fa-twitter text-xl"></i>
                        </a>
                        <a href="https://linkedin.com/in/username" class="text-gray-400 hover:text-white transition-colors">
                            <i class="fab fa-linkedin-in text-xl"></i>
                        </a>
                        <a href="https://github.com/username" class="text-gray-400 hover:text-white transition-colors">
                            <i class="fab fa-github text-xl"></i>
                        </a>
                        <a href="https://dribbble.com/username" class="text-gray-400 hover:text-white transition-colors">
                            <i class="fab fa-dribbble text-xl"></i>
                        </a>
                    </div>
                </div>
                
                <!-- Quick Links -->
                <div>
                    <h3 class="font-semibold mb-4">Quick Links</h3>
                    <ul class="space-y-2">
                        <li><a href="#home" class="text-gray-400 hover:text-white transition-colors">Home</a></li>
                        <li><a href="#about" class="text-gray-400 hover:text-white transition-colors">About</a></li>
                        <li><a href="#portfolio" class="text-gray-400 hover:text-white transition-colors">Portfolio</a></li>
                        <li><a href="#projects" class="text-gray-400 hover:text-white transition-colors">Projects</a></li>
                        <li><a href="#contact" class="text-gray-400 hover:text-white transition-colors">Contact</a></li>
                    </ul>
                </div>
                
                <!-- Services -->
                <div>
                    <h3 class="font-semibold mb-4">Services</h3>
                    <ul class="space-y-2">
                        <li class="text-gray-400">Web Development</li>
                        <li class="text-gray-400">UI/UX Design</li>
                        <li class="text-gray-400">Mobile Apps</li>
                        <li class="text-gray-400">Branding</li>
                        <li class="text-gray-400">Consulting</li>
                    </ul>
                </div>
            </div>
            
            <div class="border-t border-gray-800 mt-12 pt-8 text-center text-gray-400">
                <p>&copy; 2025 Your Brand. All rights reserved. Built with ❤️ and modern technologies.</p>
            </div>
        </div>
    </footer>

    <!-- Back to Top Button -->
    <button 
        x-show="showBackToTop" 
        @click="window.scrollTo({top: 0, behavior: 'smooth'})"
        x-transition:enter="transition ease-out duration-300"
        x-transition:enter-start="opacity-0 transform scale-90"
        x-transition:enter-end="opacity-100 transform scale-100"
        x-transition:leave="transition ease-in duration-300"
        x-transition:leave-start="opacity-100 transform scale-100"
        x-transition:leave-end="opacity-0 transform scale-90"
        class="fixed bottom-8 right-8 bg-indigo-600 hover:bg-indigo-700 text-white p-3 rounded-full shadow-lg transition-all z-40">
        <i class="fas fa-arrow-up"></i>
    </button>

    <!-- Alpine.js -->
    <script src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
    
    <!-- AOS -->
    <script src="https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.js"></script>
    
    <!-- Custom JavaScript -->
    <script>
        // Initialize AOS
        AOS.init({
            duration: 800,
            easing: 'ease-out',
            once: true,
            offset: 50
        });

// EmailJS Contact Form Handler - Playground Compatible
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('emailjs-form');
    const btn = document.getElementById('contact-btn');
    const successMsg = document.getElementById('success-message');
    const errorMsg = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    
    if (form && btn) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            
            // Change button state
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Sending...';
            
            // Hide previous messages
            successMsg.classList.add('hidden');
            errorMsg.classList.add('hidden');
            
            // EmailJS send - EXACT playground method
            const serviceID = '{{YOUR_EMAIL_JS_SERVICE_ID}}';
            const templateID = '{{YOUR_EMAIL_JS_TEMPLATE_ID}}';
            
            emailjs.sendForm(serviceID, templateID, form)
                .then(function(response) {
                    console.log('EmailJS SUCCESS:', response.status, response.text);
                    
                    // Show success message
                    successMsg.classList.remove('hidden');
                    
                    // Reset form
                    form.reset();
                    
                    // Reset button
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-paper-plane mr-2"></i>Send Message';
                    
                    // Hide success message after 5 seconds
                    setTimeout(() => {
                        successMsg.classList.add('hidden');
                    }, 5000);
                    
                }, function(error) {
                    console.log('EmailJS FAILED:', error);
                    
                    // Show error message with details
                    let errorMessage = 'Failed to send message. Please try again.';
                    if (error.status === 422) {
                        errorMessage = 'Invalid template or service configuration.';
                    } else if (error.status === 412) {
                        errorMessage = 'Email service authentication error.';
                    } else if (error.status === 400) {
                        errorMessage = 'Invalid request. Please check your inputs.';
                    }
                    
                    errorText.textContent = errorMessage;
                    errorMsg.classList.remove('hidden');
                    
                    // Reset button
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-paper-plane mr-2"></i>Send Message';
                });
        });
    } else {
        console.error('EmailJS form elements not found!');
    }
});

        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Update active navigation link on scroll
        window.addEventListener('scroll', () => {
            const sections = document.querySelectorAll('section[id]');
            const navLinks = document.querySelectorAll('.nav-link');
            
            let current = '';
            sections.forEach(section => {
                const sectionTop = section.offsetTop;
                const sectionHeight = section.clientHeight;
                if (scrollY >= (sectionTop - 200)) {
                    current = section.getAttribute('id');
                }
            });

            navLinks.forEach(link => {
                link.classList.remove('text-indigo-600', 'dark:text-indigo-400');
                link.classList.add('text-gray-700', 'dark:text-gray-300');
                
                if (link.getAttribute('href') === `#${current}`) {
                    link.classList.remove('text-gray-700', 'dark:text-gray-300');
                    link.classList.add('text-indigo-600', 'dark:text-indigo-400');
                }
            });
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            const mobileMenu = document.querySelector('.mobile-menu');
            const hamburger = document.querySelector('.hamburger');
            
            if (!mobileMenu.contains(event.target) && !hamburger.contains(event.target)) {
                // Close mobile menu logic would go here
            }
        });
    </script>
</body>
</html>
"""