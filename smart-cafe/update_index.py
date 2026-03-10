import re
import os

filepath = r"c:\Users\Warlock\Desktop\COMSATS_SmartCafe2 - Copy\COMSATS_SmartCafe\frontend\templates\index.html"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

new_styles = """    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <!-- FontAwesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" />

    <style>
      :root {
        --primary: #FF7E00; /* Vivid, appealing orange */
        --primary-glow: rgba(255, 126, 0, 0.4);
        --bg-dark: #09090b; /* Zinc 950 for deep sleek background */
        --card-bg: rgba(255, 255, 255, 0.03); /* Glassmorphism base */
        --card-border: rgba(255, 255, 255, 0.08);
        --text-white: #fafafa;
        --text-muted: #a1a1aa;
      }

      * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
        scroll-behavior: smooth;
      }

      body {
        font-family: 'Outfit', 'Inter', sans-serif;
        color: var(--text-white);
        background: var(--bg-dark);
        overflow-x: hidden;
        position: relative;
      }

      /* Dynamic glowing background blobs */
      body::before {
        content: '';
        position: fixed;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 50% 50%, rgba(255, 126, 0, 0.05) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(255, 200, 0, 0.03) 0%, transparent 40%);
        z-index: -1;
        pointer-events: none;
      }

      /* Subtle background image overlay */
      body::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(to bottom, rgba(9, 9, 11, 0.85), rgba(9, 9, 11, 0.95)), url("/static/images/123.jpeg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        z-index: -2;
      }

      /* --- NAVBAR --- */
      .navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 5vw;
        position: fixed; /* Fixed for modern feel */
        width: 100%;
        top: 0;
        z-index: 100;
        background: rgba(9, 9, 11, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-bottom: 1px solid var(--card-border);
        transition: all 0.3s ease;
      }

      .logo {
        display: flex;
        align-items: center;
        gap: 15px;
        font-size: 1.5rem;
        font-weight: 800;
        color: white;
        text-transform: uppercase;
        letter-spacing: 1px;
      }

      .logo img {
        height: 50px;
        border-radius: 50%;
        border: 2px solid transparent; /* Hide initial border to use box-shadow glow */
        box-shadow: 0 0 15px var(--primary-glow);
        transition: transform 0.4s ease, box-shadow 0.4s ease;
      }

      .logo:hover img {
        transform: rotate(360deg);
        box-shadow: 0 0 25px var(--primary);
      }

      .logo span {
        color: var(--primary);
        background: linear-gradient(90deg, #FF7E00, #FFB347);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
      }

      /* --- HERO SECTION --- */
      .hero-section {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 100px 5vw 0;
        position: relative;
      }

      .hero-text {
        flex: 1;
        z-index: 2;
        animation: fadeUp 1s ease-out forwards;
      }

      @keyframes fadeUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
      }

      .hero-text h2 {
        font-size: 1.5rem;
        color: var(--primary);
        margin-bottom: 15px;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
      }

      .hero-text h1 {
        font-family: 'Outfit', sans-serif;
        font-size: 4.5rem;
        line-height: 1.1;
        margin-bottom: 25px;
        font-weight: 800;
        background: linear-gradient(180deg, #ffffff 0%, #a1a1aa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
      }

      .hero-text p {
        color: var(--text-muted);
        font-size: 1.15rem;
        max-width: 500px;
        margin-bottom: 40px;
        line-height: 1.7;
      }

      .btn-main {
        background: linear-gradient(135deg, #FF7E00 0%, #E65C00 100%);
        color: white;
        padding: 18px 45px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: 700;
        font-size: 1.1rem;
        display: inline-block;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        box-shadow: 0 10px 25px var(--primary-glow);
        position: relative;
        overflow: hidden;
      }

      .btn-main::before {
        content: '';
        position: absolute;
        top: 0; left: -100%; width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
      }

      .btn-main:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(255, 126, 0, 0.5);
      }

      .btn-main:hover::before {
        left: 100%;
      }

      /* Hero Image Style */
      .hero-img-container {
        flex: 1;
        display: flex;
        justify-content: center;
        position: relative;
        animation: fadeInRight 1.2s ease-out forwards;
      }

      @keyframes fadeInRight {
        from { opacity: 0; transform: translateX(50px); }
        to { opacity: 1; transform: translateX(0); }
      }

      .hero-img {
        width: 450px;
        height: 450px;
        object-fit: cover;
        border-radius: 50%;
        border: 4px solid transparent;
        background: linear-gradient(var(--bg-dark), var(--bg-dark)) padding-box,
                    linear-gradient(135deg, var(--primary), #FFB347) border-box;
        padding: 15px;
        box-shadow: 0 0 50px rgba(255, 126, 0, 0.2);
        animation: float 6s ease-in-out infinite;
      }

      @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
        100% { transform: translateY(0px); }
      }

      /* --- ROLES SECTION --- */
      .roles-section {
        padding: 120px 5vw;
        text-align: center;
        position: relative;
      }

      .section-title {
        font-size: 3rem;
        margin-bottom: 70px;
        font-weight: 800;
      }

      .section-title span {
        color: var(--primary);
        position: relative;
      }

      .section-title span::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 0;
        width: 100%;
        height: 4px;
        background: var(--primary);
        border-radius: 2px;
      }

      .role-grid {
        display: flex;
        justify-content: center;
        gap: 40px;
        flex-wrap: wrap;
      }

      .role-card {
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid var(--card-border);
        width: 320px;
        padding: 50px 30px;
        border-radius: 24px;
        text-decoration: none;
        color: white;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
      }

      .role-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(circle at top right, rgba(255, 126, 0, 0.1), transparent 70%);
        opacity: 0;
        transition: opacity 0.4s ease;
      }

      .role-card:hover {
        transform: translateY(-15px) scale(1.02);
        border-color: rgba(255, 126, 0, 0.3);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 20px var(--primary-glow);
      }

      .role-card:hover::before {
        opacity: 1;
      }

      .icon-box {
        font-size: 3.5rem;
        margin-bottom: 25px;
        display: inline-block;
        transition: transform 0.4s ease;
        filter: drop-shadow(0 5px 15px rgba(255, 126, 0, 0.3));
      }

      .role-card:hover .icon-box {
        transform: scale(1.15) rotate(5deg);
      }

      .role-card h3 {
        font-size: 1.6rem;
        margin-bottom: 12px;
        font-weight: 700;
      }

      .role-card p {
        font-size: 1rem;
        color: var(--text-muted);
        margin-bottom: 30px;
        line-height: 1.5;
        position: relative;
        z-index: 1;
      }

      .arrow-link {
        color: var(--primary);
        font-weight: 600;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        transition: gap 0.3s ease;
        position: relative;
        z-index: 1;
      }

      .role-card:hover .arrow-link {
        gap: 15px;
      }

      /* Corner Ribbon */
      .ribbon {
        position: fixed;
        top: 0;
        left: 0;
        width: 150px;
        height: 150px;
        overflow: hidden;
        z-index: 1000;
        pointer-events: none;
      }

      .ribbon::before {
        content: "Smart Cafe";
        position: absolute;
        width: 150%;
        height: 40px;
        background: linear-gradient(90deg, #FF7E00, #E65C00);
        transform: rotate(-45deg) translateY(-20px);
        display: flex;
        justify-content: center;
        align-items: center;
        font-weight: 800;
        font-family: 'Outfit', sans-serif;
        color: white;
        top: 35px;
        left: -40px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
        letter-spacing: 1px;
      }

      /* --- UNIVERSAL FOOTER STYLE --- */
      .main-footer {
        background: linear-gradient(to top, #000000, rgba(9, 9, 11, 0.8));
        color: var(--text-muted);
        padding: 80px 0 20px;
        position: relative;
        font-family: "Inter", sans-serif;
        border-top: 1px solid var(--card-border);
      }

      .main-footer::before {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 100%; height: 2px;
        background: linear-gradient(90deg, transparent, var(--primary), transparent);
      }

      .footer-container {
        max-width: 1200px;
        margin: 0 auto;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 40px;
        padding: 0 5vw;
      }

      .footer-col h3 {
        color: white;
        font-size: 1.3rem;
        margin-bottom: 25px;
        font-weight: 600;
        position: relative;
        display: inline-block;
      }

      .footer-col h3::after {
        content: "";
        position: absolute;
        left: 0;
        bottom: -8px;
        width: 40px;
        height: 3px;
        background: var(--primary);
        border-radius: 2px;
      }

      .footer-col p {
        font-size: 0.95rem;
        line-height: 1.8;
        margin-bottom: 15px;
      }

      .footer-links {
        list-style: none;
      }

      .footer-links li {
        margin-bottom: 12px;
      }

      .footer-links a {
        color: var(--text-muted);
        text-decoration: none;
        transition: all 0.3s ease;
        display: inline-block;
      }

      .footer-links a:hover {
        color: var(--primary);
        transform: translateX(8px);
      }

      .social-icons {
        display: flex;
        gap: 15px;
        margin-top: 20px;
      }

      .social-icons a {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 50%;
        color: white;
        font-size: 1.1rem;
        transition: all 0.3s ease;
      }

      .social-icons a:hover {
        background: var(--primary);
        border-color: var(--primary);
        transform: translateY(-5px);
        box-shadow: 0 10px 20px var(--primary-glow);
      }

      .footer-bottom {
        text-align: center;
        padding-top: 30px;
        margin-top: 60px;
        border-top: 1px solid var(--card-border);
        font-size: 0.9rem;
      }

      /* Mobile Responsive */
      @media (max-width: 991px) {
        .hero-section {
          flex-direction: column-reverse;
          padding: 150px 5vw 80px;
          text-align: center;
        }
        .hero-text h1 {
          font-size: 3.5rem;
        }
        .hero-text p {
          margin: 0 auto 30px;
        }
        .hero-img {
          width: 350px;
          height: 350px;
          margin-bottom: 50px;
        }
      }

      @media (max-width: 768px) {
        .hero-text h1 {
          font-size: 2.8rem;
        }
        .hero-img {
          width: 280px;
          height: 280px;
        }
        .section-title {
          font-size: 2.2rem;
        }
        .navbar {
          position: relative;
          padding: 15px 5vw;
          background: rgba(9, 9, 11, 0.9);
        }
        .logo {
          font-size: 1.2rem;
        }
        .logo img {
          height: 40px;
        }
      }
    </style>"""

# Using regex to replace everything from the first <link or <style> up to </style>
pattern = re.compile(r'<link.*?</style>', re.DOTALL)
new_content = pattern.sub(new_styles, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Updated index.html CSS successfully!")
