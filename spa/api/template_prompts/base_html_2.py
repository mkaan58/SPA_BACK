BASE_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    <title>Professional Website - Dark Mode Template</title>
    <meta name="description" content="Modern responsive website with advanced interactive features">
    
    <!-- Performance optimized CDN loading -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Core CSS Libraries -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link href="https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css">
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- EmailJS -->
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/@emailjs/browser@4/dist/email.min.js"></script>
    <script>
        if (typeof emailjs !== 'undefined') {
            emailjs.init("{{ YOUR_EMAIL_JS_PUBLIC_KEY }}");
        }
    </script>
    
    <!-- Enhanced Dark Mode Styles -->
    <style>
        :root {
            --bg-primary: #0F0F0F;
            --bg-secondary: #1A1A1A;
            --bg-card: #242424;
            --text-primary: #FFFFFF;
            --text-secondary: #E5E5E5;
            --text-muted: #A3A3A3;
            --accent-blue: #3B82F6;
            --accent-purple: #8B5CF6;
            --accent-green: #10B981;
            --border-color: #333333;
            --font-heading: 'Playfair Display', serif;
            --font-body: 'Inter', sans-serif;
        }
        
        * { box-sizing: border-box; }
        
        body {
            background-color: var(--bg-primary);
            color: var(--text-primary);
            font-family: var(--font-body);
            line-height: 1.6;
            margin: 0;
            overflow-x: hidden;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-heading);
            color: var(--text-primary);
            font-weight: 700;
            line-height: 1.3;
        }
        
        p { color: var(--text-secondary); font-size: 1.1rem; }
        
        /* Navigation */
        .navbar {
            background: rgba(15, 15, 15, 0.95);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--border-color);
            position: fixed;
            top: 0;
            width: 100%;
            z-index: 1000;
            transition: all 0.3s ease;
        }
        
        .nav-link {
            color: var(--text-secondary);
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 6px;
            transition: all 0.3s ease;
        }
        
        .nav-link:hover, .nav-link.active {
            color: var(--accent-blue);
            background: rgba(59, 130, 246, 0.1);
        }
        
        /* Buttons */
        .btn-primary {
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            transition: all 0.3s ease;
            min-height: 48px;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
        }
        
        .btn-secondary {
            background: transparent;
            color: var(--accent-blue);
            border: 2px solid var(--accent-blue);
            padding: 10px 22px;
            border-radius: 8px;
            font-weight: 600;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            transition: all 0.3s ease;
            min-height: 48px;
        }
        
        .btn-secondary:hover {
            background: var(--accent-blue);
            color: white;
            transform: translateY(-2px);
        }
        
        /* Cards */
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            transition: all 0.3s ease;
            height: 100%;
        }
        
        .card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 40px rgba(59, 130, 246, 0.2);
            border-color: var(--accent-blue);
        }
        
        /* Forms */
        .form-control {
            background: var(--bg-card);
            border: 2px solid var(--border-color);
            color: var(--text-primary);
            border-radius: 8px;
            padding: 12px 16px;
            width: 100%;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        .form-control:focus {
            outline: none;
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        .form-control::placeholder { color: var(--text-muted); }
        
        .form-label {
            color: var(--text-primary);
            font-weight: 600;
            margin-bottom: 8px;
            display: block;
        }
        
        /* Mobile Menu */
        .mobile-menu {
            position: fixed;
            top: 64px;
            right: 0;
            height: calc(100vh - 64px);
            width: 280px;
            background: var(--bg-primary);
            border-left: 1px solid var(--border-color);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 999;
        }
        
        .mobile-menu.active { transform: translateX(0); }
        
        .hamburger {
            display: flex;
            flex-direction: column;
            width: 24px;
            height: 24px;
            background: transparent;
            border: none;
            cursor: pointer;
            justify-content: space-around;
        }
        
        .hamburger span {
            width: 100%;
            height: 2px;
            background: var(--text-primary);
            transition: all 0.3s ease;
        }
        
        .hamburger.active span:nth-child(1) { transform: rotate(45deg) translate(5px, 5px); }
        .hamburger.active span:nth-child(2) { opacity: 0; }
        .hamburger.active span:nth-child(3) { transform: rotate(-45deg) translate(7px, -6px); }
        
        /* Swiper */
        .swiper {
            padding: 20px 0 60px 0;
            overflow: visible;
        }
        
        .swiper-pagination-bullet {
            background: var(--text-muted);
            opacity: 0.5;
        }
        
        .swiper-pagination-bullet-active {
            background: var(--accent-blue);
            opacity: 1;
        }
        
        .swiper-button-next,
        .swiper-button-prev {
            color: var(--accent-blue);
            background: var(--bg-card);
            width: 44px;
            height: 44px;
            border-radius: 50%;
            border: 1px solid var(--border-color);
        }
        
        @media (max-width: 767px) {
            .swiper-button-next,
            .swiper-button-prev { display: none; }
        }
        
        /* Utilities */
        .hover-lift:hover { transform: translateY(-5px); }
        .text-gradient { background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        
        /* Responsive */
        @media (max-width: 768px) {
            h1 { font-size: 2rem; }
            h2 { font-size: 1.75rem; }
            .btn-primary, .btn-secondary { min-height: 48px; font-size: 16px; }
            .form-control { font-size: 16px; padding: 16px; }
        }
    </style>
</head>

<body x-data="{ mobileMenuOpen: false, showBackToTop: false }" x-init="
    window.addEventListener('scroll', () => {
        showBackToTop = window.scrollY > 300;
    });
">

    <!-- Navigation -->
    <nav class="navbar">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <a href="#home" class="font-bold text-2xl" style="font-family: var(--font-heading); color: var(--text-primary);">Professional Brand</a>
                
                <!-- Desktop Navigation -->
                <div class="hidden md:flex space-x-8">
                    <a href="#home" class="nav-link active">Home</a>
                    <a href="#about" class="nav-link">About</a>
                    <a href="#portfolio" class="nav-link">Portfolio</a>
                    <a href="#services" class="nav-link">Services</a>
                    <a href="#contact" class="nav-link">Contact</a>
                </div>
                
                <!-- Mobile menu button -->
                <div class="md:hidden">
                    <button @click="mobileMenuOpen = !mobileMenuOpen" class="hamburger" :class="{ 'active': mobileMenuOpen }">
                        <span></span>
                        <span></span>
                        <span></span>
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Mobile Navigation -->
        <div class="mobile-menu md:hidden" :class="{ 'active': mobileMenuOpen }">
            <div class="px-4 py-2">
                <a href="#home" @click="mobileMenuOpen = false" class="nav-link block">Home</a>
                <a href="#about" @click="mobileMenuOpen = false" class="nav-link block">About</a>
                <a href="#portfolio" @click="mobileMenuOpen = false" class="nav-link block">Portfolio</a>
                <a href="#services" @click="mobileMenuOpen = false" class="nav-link block">Services</a>
                <a href="#contact" @click="mobileMenuOpen = false" class="nav-link block">Contact</a>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section id="home" class="min-h-screen flex items-center justify-center relative">
        <div id="particles-js" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: -1;"></div>
        
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <div data-aos="fade-up" data-aos-duration="1000">
                <h1 class="text-4xl md:text-6xl font-bold mb-6">
                    Welcome to <span id="typed-text" class="text-gradient"></span>
                </h1>
                <p class="text-xl md:text-2xl mb-8 max-w-3xl mx-auto" style="color: var(--text-secondary);">
                    Creating innovative digital experiences with cutting-edge technology and stunning visual design.
                </p>
                <div class="flex flex-col sm:flex-row gap-4 justify-center">
                    <a href="#portfolio" class="btn-primary">
                        <i class="fas fa-rocket mr-2"></i>
                        View My Work
                    </a>
                    <a href="#contact" class="btn-secondary">
                        <i class="fas fa-envelope mr-2"></i>
                        Get In Touch
                    </a>
                </div>
            </div>
        </div>
    </section>

    <!-- About Section -->
    <section id="about" class="py-20" style="background-color: var(--bg-secondary);">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center mb-16" data-aos="fade-up">
                <h2 class="text-3xl md:text-4xl font-bold mb-4">About Me</h2>
                <p class="text-xl max-w-3xl mx-auto">Passionate about creating digital experiences that make a difference</p>
            </div>
            
            <div class="grid lg:grid-cols-2 gap-12 items-center">
                <div data-aos="fade-right">
                    <img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500&h=600&fit=crop&auto=format" 
                         alt="Profile" class="rounded-2xl shadow-2xl w-full max-w-md mx-auto hover-lift" loading="lazy">
                </div>
                
                <div data-aos="fade-left">
                    <h3 class="text-2xl font-bold mb-6">Creative Developer & Designer</h3>
                    <p class="mb-6 leading-relaxed">
                        With over 5 years of experience in web development and design, I specialize in creating 
                        modern, responsive websites that not only look stunning but also provide exceptional user experiences.
                    </p>
                    
                    <div class="grid grid-cols-2 gap-4 mb-8">
                        <div class="text-center card">
                            <div class="text-2xl font-bold" style="color: var(--accent-blue);">50+</div>
                            <div class="text-sm" style="color: var(--text-muted);">Projects Completed</div>
                        </div>
                        <div class="text-center card">
                            <div class="text-2xl font-bold" style="color: var(--accent-blue);">5+</div>
                            <div class="text-sm" style="color: var(--text-muted);">Years Experience</div>
                        </div>
                    </div>
                    
                    <div class="flex flex-wrap gap-3">
                        <span class="px-3 py-1 rounded-full text-sm" style="background: rgba(59, 130, 246, 0.2); color: var(--accent-blue);">JavaScript</span>
                        <span class="px-3 py-1 rounded-full text-sm" style="background: rgba(59, 130, 246, 0.2); color: var(--accent-blue);">React</span>
                        <span class="px-3 py-1 rounded-full text-sm" style="background: rgba(59, 130, 246, 0.2); color: var(--accent-blue);">UI/UX Design</span>
                        <span class="px-3 py-1 rounded-full text-sm" style="background: rgba(59, 130, 246, 0.2); color: var(--accent-blue);">Tailwind CSS</span>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Portfolio Section with Swiper -->
    <section id="portfolio" class="py-20">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center mb-16" data-aos="fade-up">
                <h2 class="text-3xl md:text-4xl font-bold mb-4">Portfolio</h2>
                <p class="text-xl max-w-3xl mx-auto">A showcase of my latest work and creative projects</p>
            </div>
            
            <div class="swiper portfolio-swiper" data-aos="fade-up" data-aos-delay="200">
                <div class="swiper-wrapper">
                    <div class="swiper-slide">
                        <div class="card hover-lift">
                            <img src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&h=300&fit=crop&auto=format" 
                                 alt="E-commerce Platform" class="w-full h-48 object-cover rounded-lg mb-4" loading="lazy">
                            <h3 class="text-xl font-bold mb-2">E-commerce Platform</h3>
                            <p style="color: var(--text-secondary);">Modern online shopping experience with advanced features</p>
                        </div>
                    </div>
                    <div class="swiper-slide">
                        <div class="card hover-lift">
                            <img src="https://images.unsplash.com/photo-1551650975-87deedd944c3?w=600&h=300&fit=crop&auto=format" 
                                 alt="Mobile App Design" class="w-full h-48 object-cover rounded-lg mb-4" loading="lazy">
                            <h3 class="text-xl font-bold mb-2">Mobile App Design</h3>
                            <p style="color: var(--text-secondary);">Intuitive mobile interface with seamless user experience</p>
                        </div>
                    </div>
                    <div class="swiper-slide">
                        <div class="card hover-lift">
                            <img src="https://images.unsplash.com/photo-1558655146-9f40138edfeb?w=600&h=300&fit=crop&auto=format" 
                                 alt="Brand Identity" class="w-full h-48 object-cover rounded-lg mb-4" loading="lazy">
                            <h3 class="text-xl font-bold mb-2">Brand Identity</h3>
                            <p style="color: var(--text-secondary);">Complete branding solution with logo and visual system</p>
                        </div>
                    </div>
                    <div class="swiper-slide">
                        <div class="card hover-lift">
                            <img src="https://images.unsplash.com/photo-1499951360447-b19be8fe80f5?w=600&h=300&fit=crop&auto=format" 
                                 alt="Web Application" class="w-full h-48 object-cover rounded-lg mb-4" loading="lazy">
                            <h3 class="text-xl font-bold mb-2">Web Application</h3>
                            <p style="color: var(--text-secondary);">Full-stack web application with modern architecture</p>
                        </div>
                    </div>
                    <div class="swiper-slide">
                        <div class="card hover-lift">
                            <img src="https://images.unsplash.com/photo-1586717791821-3f44a563fa4c?w=600&h=300&fit=crop&auto=format" 
                                 alt="Dashboard Design" class="w-full h-48 object-cover rounded-lg mb-4" loading="lazy">
                            <h3 class="text-xl font-bold mb-2">Dashboard Design</h3>
                            <p style="color: var(--text-secondary);">Clean and intuitive admin dashboard interface</p>
                        </div>
                    </div>
                    <div class="swiper-slide">
                        <div class="card hover-lift">
                            <img src="https://images.unsplash.com/photo-1557804506-669a67965ba0?w=600&h=300&fit=crop&auto=format" 
                                 alt="Website Redesign" class="w-full h-48 object-cover rounded-lg mb-4" loading="lazy">
                            <h3 class="text-xl font-bold mb-2">Website Redesign</h3>
                            <p style="color: var(--text-secondary);">Complete website makeover with improved UX</p>
                        </div>
                    </div>
                </div>
                <div class="swiper-pagination"></div>
                <div class="swiper-button-next"></div>
                <div class="swiper-button-prev"></div>
            </div>
        </div>
    </section>

    <!-- Services Section -->
    <section id="services" class="py-20" style="background-color: var(--bg-secondary);">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center mb-16" data-aos="fade-up">
                <h2 class="text-3xl md:text-4xl font-bold mb-4">Services</h2>
                <p class="text-xl max-w-3xl mx-auto">Comprehensive digital solutions tailored to your needs</p>
            </div>
            
            <div class="grid md:grid-cols-3 gap-8">
                <div class="card hover-lift text-center" data-aos="fade-up" data-aos-delay="100">
                    <div class="w-16 h-16 mx-auto mb-6 rounded-lg flex items-center justify-center" style="background: rgba(59, 130, 246, 0.2);">
                        <i class="fas fa-code text-2xl" style="color: var(--accent-blue);"></i>
                    </div>
                    <h3 class="text-xl font-bold mb-4">Web Development</h3>
                    <p style="color: var(--text-secondary);">Custom websites and web applications built with modern technologies.</p>
                </div>
                
                <div class="card hover-lift text-center" data-aos="fade-up" data-aos-delay="200">
                    <div class="w-16 h-16 mx-auto mb-6 rounded-lg flex items-center justify-center" style="background: rgba(139, 92, 246, 0.2);">
                        <i class="fas fa-palette text-2xl" style="color: var(--accent-purple);"></i>
                    </div>
                    <h3 class="text-xl font-bold mb-4">UI/UX Design</h3>
                    <p style="color: var(--text-secondary);">User-centered design solutions that create meaningful experiences.</p>
                </div>
                
                <div class="card hover-lift text-center" data-aos="fade-up" data-aos-delay="300">
                    <div class="w-16 h-16 mx-auto mb-6 rounded-lg flex items-center justify-center" style="background: rgba(16, 185, 129, 0.2);">
                        <i class="fas fa-mobile-alt text-2xl" style="color: var(--accent-green);"></i>
                    </div>
                    <h3 class="text-xl font-bold mb-4">Mobile Development</h3>
                    <p style="color: var(--text-secondary);">Cross-platform mobile applications that work seamlessly.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Contact Section -->
    <section id="contact" class="py-20">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center mb-16" data-aos="fade-up">
                <h2 class="text-3xl md:text-4xl font-bold mb-4">Get In Touch</h2>
                <p class="text-xl max-w-3xl mx-auto">Let's discuss your next project and bring your ideas to life</p>
            </div>
            
            <div class="grid lg:grid-cols-2 gap-12">
                <!-- Contact Info -->
                <div data-aos="fade-right">
                    <h3 class="text-2xl font-bold mb-8">Let's Connect</h3>
                    <div class="space-y-6">
                        <div class="flex items-center">
                            <div class="w-12 h-12 rounded-lg flex items-center justify-center mr-4" style="background: rgba(59, 130, 246, 0.2);">
                                <i class="fas fa-envelope" style="color: var(--accent-blue);"></i>
                            </div>
                            <div>
                                <h4 class="font-semibold">Email</h4>
                                <p style="color: var(--text-secondary);">hello@example.com</p>
                            </div>
                        </div>
                        <div class="flex items-center">
                            <div class="w-12 h-12 rounded-lg flex items-center justify-center mr-4" style="background: rgba(59, 130, 246, 0.2);">
                                <i class="fas fa-phone" style="color: var(--accent-blue);"></i>
                            </div>
                            <div>
                                <h4 class="font-semibold">Phone</h4>
                                <p style="color: var(--text-secondary);">+1 (555) 123-4567</p>
                            </div>
                        </div>
                        <div class="flex items-center">
                            <div class="w-12 h-12 rounded-lg flex items-center justify-center mr-4" style="background: rgba(59, 130, 246, 0.2);">
                                <i class="fas fa-map-marker-alt" style="color: var(--accent-blue);"></i>
                            </div>
                            <div>
                                <h4 class="font-semibold">Location</h4>
                                <p style="color: var(--text-secondary);">San Francisco, CA</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Contact Form -->
                <div data-aos="fade-left">
                    <div class="card">
                        <h3 class="text-xl font-bold mb-6">Send Message</h3>
                        
                        <form id="emailjs-form" class="space-y-6">
                            <div class="grid md:grid-cols-2 gap-6">
                                <div class="field">
                                    <label for="name" class="form-label">
                                        <i class="fas fa-user mr-2"></i>Name
                                    </label>
                                    <input type="text" name="name" id="name" required class="form-control" placeholder="Your Name">
                                </div>
                                <div class="field">
                                    <label for="email" class="form-label">
                                        <i class="fas fa-envelope mr-2"></i>Email
                                    </label>
                                    <input type="email" name="email" id="email" required class="form-control" placeholder="your@email.com">
                                </div>
                            </div>
                            <div class="field">
                                <label for="subject" class="form-label">
                                    <i class="fas fa-tag mr-2"></i>Subject
                                </label>
                                <input type="text" name="subject" id="subject" required class="form-control" placeholder="Project Inquiry">
                            </div>
                            <div class="field">
                                <label for="message" class="form-label">
                                    <i class="fas fa-comment mr-2"></i>Message
                                </label>
                                <textarea name="message" id="message" required rows="5" class="form-control" placeholder="Tell me about your project..."></textarea>
                            </div>
                            
                            <div class="field hidden">
                                <input type="hidden" name="to_email" id="to_email" value="USER_EMAIL_PLACEHOLDER">
                            </div>
                            
                            <button type="submit" id="contact-btn" class="btn-primary w-full">
                                <i class="fas fa-paper-plane mr-2"></i>
                                Send Message
                            </button>
                            
                            <div id="success-message" class="hidden text-center py-3 rounded-lg" style="color: var(--accent-green); background: rgba(16, 185, 129, 0.1);">
                                <i class="fas fa-check-circle mr-2"></i>
                                Message sent successfully! I'll get back to you soon.
                            </div>
                            <div id="error-message" class="hidden text-center py-3 rounded-lg" style="color: #EF4444; background: rgba(239, 68, 68, 0.1);">
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
<footer class="py-12" style="background-color: var(--bg-primary); border-top: 1px solid var(--border-color);">
   <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
       <div class="grid md:grid-cols-4 gap-8">
           <div class="md:col-span-2">
               <div class="text-2xl font-bold mb-4" style="font-family: var(--font-heading); color: var(--accent-blue);">Professional Brand</div>
               <p class="mb-6 max-w-md" style="color: var(--text-secondary);">
                   Creating digital experiences that inspire and connect. Let's build something amazing together.
               </p>
               <div class="flex space-x-4">
                   <a href="#" class="w-10 h-10 rounded-lg flex items-center justify-center transition-all" style="background: var(--bg-card); color: var(--text-muted);" onmouseover="this.style.color='var(--accent-blue)'" onmouseout="this.style.color='var(--text-muted)'">
                       <i class="fab fa-twitter"></i>
                   </a>
                   <a href="#" class="w-10 h-10 rounded-lg flex items-center justify-center transition-all" style="background: var(--bg-card); color: var(--text-muted);" onmouseover="this.style.color='var(--accent-blue)'" onmouseout="this.style.color='var(--text-muted)'">
                       <i class="fab fa-linkedin-in"></i>
                   </a>
                   <a href="#" class="w-10 h-10 rounded-lg flex items-center justify-center transition-all" style="background: var(--bg-card); color: var(--text-muted);" onmouseover="this.style.color='var(--accent-blue)'" onmouseout="this.style.color='var(--text-muted)'">
                       <i class="fab fa-github"></i>
                   </a>
                   <a href="#" class="w-10 h-10 rounded-lg flex items-center justify-center transition-all" style="background: var(--bg-card); color: var(--text-muted);" onmouseover="this.style.color='var(--accent-blue)'" onmouseout="this.style.color='var(--text-muted)'">
                       <i class="fab fa-dribbble"></i>
                   </a>
               </div>
           </div>
           
           <div>
               <h3 class="font-semibold mb-4">Quick Links</h3>
               <ul class="space-y-2">
                   <li><a href="#home" class="transition-colors" style="color: var(--text-muted);" onmouseover="this.style.color='var(--text-primary)'" onmouseout="this.style.color='var(--text-muted)'">Home</a></li>
                   <li><a href="#about" class="transition-colors" style="color: var(--text-muted);" onmouseover="this.style.color='var(--text-primary)'" onmouseout="this.style.color='var(--text-muted)'">About</a></li>
                   <li><a href="#portfolio" class="transition-colors" style="color: var(--text-muted);" onmouseover="this.style.color='var(--text-primary)'" onmouseout="this.style.color='var(--text-muted)'">Portfolio</a></li>
                   <li><a href="#services" class="transition-colors" style="color: var(--text-muted);" onmouseover="this.style.color='var(--text-primary)'" onmouseout="this.style.color='var(--text-muted)'">Services</a></li>
                   <li><a href="#contact" class="transition-colors" style="color: var(--text-muted);" onmouseover="this.style.color='var(--text-primary)'" onmouseout="this.style.color='var(--text-muted)'">Contact</a></li>
               </ul>
           </div>
           
           <div>
               <h3 class="font-semibold mb-4">Services</h3>
               <ul class="space-y-2" style="color: var(--text-muted);">
                   <li>Web Development</li>
                   <li>UI/UX Design</li>
                   <li>Mobile Apps</li>
                   <li>Branding</li>
                   <li>Consulting</li>
               </ul>
           </div>
       </div>
       
       <div class="mt-12 pt-8 text-center" style="border-top: 1px solid var(--border-color); color: var(--text-muted);">
           <p>&copy; 2025 Professional Brand. All rights reserved. Built with ❤️ and modern technologies.</p>
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
   class="fixed bottom-8 right-8 p-3 rounded-full shadow-lg transition-all z-40"
   style="background: var(--accent-blue); color: white;"
   onmouseover="this.style.transform='scale(1.1)'"
   onmouseout="this.style.transform='scale(1)'">
   <i class="fas fa-arrow-up"></i>
</button>

<!-- JavaScript CDNs -->
<script src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
<script src="https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.js"></script>
<script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/typed.js@2.1.0/dist/typed.umd.js"></script>

<!-- Load particles only on desktop -->
<script>
   if (window.innerWidth > 768 && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
       const script = document.createElement('script');
       script.src = 'https://cdn.jsdelivr.net/npm/particles.js@2.0.0/particles.min.js';
       document.body.appendChild(script);
   }
</script>

<!-- Enhanced JavaScript -->
<script>
   document.addEventListener('DOMContentLoaded', function() {
       // Initialize AOS
       AOS.init({
           duration: 600,
           easing: 'ease-out',
           once: true,
           offset: 50,
           disable: function() {
               return window.innerWidth < 768;
           }
       });
       
       // Initialize Typed.js
       if (document.getElementById('typed-text')) {
           new Typed('#typed-text', {
               strings: ['Modern Design', 'Web Development', 'UI/UX Design', 'Digital Innovation'],
               typeSpeed: 80,
               backSpeed: 50,
               backDelay: 2000,
               startDelay: 500,
               loop: true,
               showCursor: true,
               cursorChar: '|'
           });
       }
       
       // Initialize Portfolio Swiper
       const portfolioSwiper = new Swiper('.portfolio-swiper', {
           slidesPerView: 1,
           spaceBetween: 20,
           loop: true,
           autoplay: {
               delay: 4000,
               disableOnInteraction: false,
               pauseOnMouseEnter: true,
           },
           pagination: {
               el: '.swiper-pagination',
               clickable: true,
               dynamicBullets: true,
           },
           navigation: {
               nextEl: '.swiper-button-next',
               prevEl: '.swiper-button-prev',
           },
           breakpoints: {
               320: { slidesPerView: 1, spaceBetween: 15 },
               640: { slidesPerView: 2, spaceBetween: 20 },
               1024: { slidesPerView: 3, spaceBetween: 30 },
           },
           speed: 600,
           touchRatio: 1,
           threshold: 5,
           allowTouchMove: true,
       });
       
       // Initialize Particles.js (only on desktop)
       if (typeof particlesJS !== 'undefined' && window.innerWidth > 768) {
           particlesJS('particles-js', {
               particles: {
                   number: { value: 50, density: { enable: true, value_area: 800 } },
                   color: { value: '#3B82F6' },
                   shape: { type: 'circle' },
                   opacity: { value: 0.3, random: true, anim: { enable: true, speed: 1, opacity_min: 0.1, sync: false } },
                   size: { value: 3, random: true, anim: { enable: true, speed: 2, size_min: 0.1, sync: false } },
                   line_linked: { enable: true, distance: 150, color: '#3B82F6', opacity: 0.2, width: 1 },
                   move: { enable: true, speed: 1, direction: 'none', random: false, straight: false, out_mode: 'out', bounce: false }
               },
               interactivity: {
                   detect_on: 'canvas',
                   events: { onhover: { enable: true, mode: 'repulse' }, onclick: { enable: true, mode: 'push' }, resize: true },
                   modes: { repulse: { distance: 100, duration: 0.4 }, push: { particles_nb: 4 } }
               },
               retina_detect: true
           });
       }
       
       // EmailJS Contact Form
       const form = document.getElementById('emailjs-form');
       const btn = document.getElementById('contact-btn');
       const successMsg = document.getElementById('success-message');
       const errorMsg = document.getElementById('error-message');
       const errorText = document.getElementById('error-text');
       
       if (form && btn) {
           form.addEventListener('submit', function(event) {
               event.preventDefault();
               
               btn.disabled = true;
               btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Sending...';
               
               successMsg.classList.add('hidden');
               errorMsg.classList.add('hidden');
               
               const serviceID = '{{YOUR_EMAIL_JS_SERVICE_ID}}';
               const templateID = '{{YOUR_EMAIL_JS_TEMPLATE_ID}}';
               
               emailjs.sendForm(serviceID, templateID, form)
                   .then(function(response) {
                       successMsg.classList.remove('hidden');
                       form.reset();
                       btn.disabled = false;
                       btn.innerHTML = '<i class="fas fa-paper-plane mr-2"></i>Send Message';
                       setTimeout(() => successMsg.classList.add('hidden'), 5000);
                   }, function(error) {
                       let errorMessage = 'Failed to send message. Please try again.';
                       if (error.status === 422) errorMessage = 'Invalid template or service configuration.';
                       else if (error.status === 412) errorMessage = 'Email service authentication error.';
                       else if (error.status === 400) errorMessage = 'Invalid request. Please check your inputs.';
                       
                       errorText.textContent = errorMessage;
                       errorMsg.classList.remove('hidden');
                       btn.disabled = false;
                       btn.innerHTML = '<i class="fas fa-paper-plane mr-2"></i>Send Message';
                   });
           });
       }
       
       // Smooth scrolling for navigation
       document.querySelectorAll('a[href^="#"]').forEach(anchor => {
           anchor.addEventListener('click', function (e) {
               e.preventDefault();
               const target = document.querySelector(this.getAttribute('href'));
               if (target) {
                   target.scrollIntoView({ behavior: 'smooth', block: 'start' });
               }
           });
       });
       
       // Update active navigation link
       window.addEventListener('scroll', () => {
           const sections = document.querySelectorAll('section[id]');
           const navLinks = document.querySelectorAll('.nav-link');
           
           let current = '';
           sections.forEach(section => {
               const sectionTop = section.offsetTop;
               if (scrollY >= (sectionTop - 200)) {
                   current = section.getAttribute('id');
               }
           });

           navLinks.forEach(link => {
               link.classList.remove('active');
               if (link.getAttribute('href') === `#${current}`) {
                   link.classList.add('active');
               }
           });
       });
       
       // Enhanced navbar scroll effect
       const navbar = document.querySelector('.navbar');
       window.addEventListener('scroll', function() {
           if (window.scrollY > 100) {
               navbar.style.background = 'rgba(15, 15, 15, 0.98)';
               navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.5)';
           } else {
               navbar.style.background = 'rgba(15, 15, 15, 0.95)';
               navbar.style.boxShadow = 'none';
           }
       });
   });
</script>

</body>
</html>
"""