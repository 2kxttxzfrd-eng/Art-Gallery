import streamlit as st
import os
from PIL import Image
from pillow_heif import register_heif_opener
import textwrap

# Register HEIF opener to handle .heic files
register_heif_opener()

# --- Page Configuration ---
st.set_page_config(
    page_title="Art Portfolio",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling ---
def local_css():
    st.markdown("""
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1 {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-weight: 300;
            color: #333;
        }
        h2, h3 {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-weight: 300;
            color: #444;
        }
        .stExpander {
            border: none;
            box-shadow: none;
        }
        .caption-text {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 0.2rem;
        }
        .award-text {
            font-size: 0.85rem;
            color: #d35400; /* Subtle orange/rust for awards */
            font-weight: 500;
            font-style: italic;
        }
        
        /* Philosophy Box Styling */
        .philosophy-box {
            background-color: #FFF9C4;
            padding: 20px;
            border-radius: 15px;
            color: #333;
            min-height: 300px; /* Ensure equal height */
        }
        .philosophy-box h4 {
            margin-top: 0;
            color: #444;
        }

        /* Reduce applied image size to ~90% of column width (reducing height by ~10%) */
        [data-testid="stImage"] img {
            width: 90% !important;
            margin-left: auto !important;
            margin-right: auto !important;
            display: block !important;
        }
        </style>
    """, unsafe_allow_html=True)

local_css()

# --- Data Management ---
# This dictionary mimics a database. 
# In a real scenario, you can map filenames to titles, years, media, and awards.
# User can edit this section to match their specific files.
ARTWORK_METADATA = {
    # Paintings
    "17BEDBFE-5596-4AEA-8B35-24C40735AFF2_1_105_c.jpeg": {
        "title": "Quiet Reflection", "medium": "Oil on Canvas", "year": "2024", "award": "First Place, Regional Art Show"
    },
    "2EC2C4E4-1E1E-4BEE-BE0D-3EDB005B5FFD_1_102_a.jpeg": {
        "title": "Urban Solitude", "medium": "Acrylic", "year": "2023", "award": ""
    },
    "59DC19CD-A001-4A84-B03B-5A11BFCF1587_1_102_a.jpeg": {
        "title": "Abstract Thoughts", "medium": "Mixed Media", "year": "2023", "award": "Honorable Mention"
    },
    "B12569F8-AB02-4252-9201-D381ACC06B24_1_102_a.jpeg": {
        "title": "Nature's Pattern", "medium": "Watercolor", "year": "2024", "award": ""
    },
    "EAD29E76-9D17-42CE-AB63-87A81FF7A6DB_1_102_o.jpeg": {
        "title": "Still Life with Fruits", "medium": "Oil", "year": "2022", "award": ""
    },
     # Origami
    "79B03030-AC27-4F27-B500-72F7ABA6F44E_1_105_c.jpeg": {
        "title": "Geometric Crane", "medium": "Washi Paper", "year": "2023", "award": ""
    },
    "C5292A45-2BB0-432F-BBF2-D91836ECEEF7_1_102_o.jpeg": {
        "title": "Complex Tessellation", "medium": "Elephant Hide Paper", "year": "2024", "award": "Best in Show, Craft Fair"
    },
    "E16229DD-C050-4ACA-AEE3-582B43E26CB2_1_105_c.jpeg": {
        "title": "Dragon Study", "medium": "Kraft Paper", "year": "2023", "award": ""
    },
    "FC38B5D7-4FB5-46F9-9608-DD5CD0CBA249_1_102_a.jpeg": {
        "title": "Modular Sphere", "medium": "Cardstock", "year": "2022", "award": ""
    },
    # Shoes
    "68FAB2F8-06C1-4F20-AD3F-69D959E2EEE9_1_102_o.jpeg": {
        "title": "Galaxy Walkers", "medium": "Angelus Paint on Canvas Shoes", "year": "2024", "award": "Commissioned Piece"
    },
    # Community
    "08E33AA3-CCA8-4DE0-B027-4D4454F453EF_1_102_o.jpeg": {
        "title": "Mural Project Leadership", "medium": "Community Event", "year": "2023", "award": "Community Service Award"
    },
    "3083F323-CD66-4CF8-88ED-B741EDA9B4FA_1_105_c.jpeg": {
        "title": "Art Workshop for Kids", "medium": "Teaching", "year": "2024", "award": ""
    },
    "6818B949-CBC1-4942-B161-99CDB302C821_1_102_o.jpeg": {
        "title": "Charity Auction", "medium": "Event Organizing", "year": "2023", "award": ""
    },
}

AWARDS_LIST = [
    {"title": "First Place, Regional Art Show", "year": "2024", "description": "Awarded for 'Quiet Reflection' in the Oil Painting category among 500+ entries."},
    {"title": "Best in Show, District Craft Fair", "year": "2024", "description": "Recognition for complex origami tessellation work."},
    {"title": "Community Service Award", "year": "2023", "description": "For leading the downtown mural restoration project."},
    {"title": "Honorable Mention, State Youth Art", "year": "2023", "description": "Acknowledged for experimental mixed media techniques."},
]

# --- Helper Functions ---
def load_image(image_path):
    try:
        image = Image.open(image_path)
        return image
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

def get_metadata(filename):
    if filename in ARTWORK_METADATA:
        return ARTWORK_METADATA[filename]
        
    # Fallback: Use filename as title if metadata is missing
    title = os.path.splitext(filename)[0]
    return {"title": title, "medium": "Unknown Medium", "year": "N/A", "award": ""}

def display_gallery(folder_path, col_width=3):
    """
    Displays images from a folder in a grid.
    col_width: Number of columns for the grid.
    """
    if not os.path.exists(folder_path):
        st.info(f"Folder not found: {folder_path}")
        return

    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.heic'))]
    files.sort() # Ensure consistent order

    if not files:
        st.info("No images found in this gallery.")
        return

    # Create grid
    cols = st.columns(col_width)
    
    for idx, file in enumerate(files):
        with cols[idx % col_width]:
            img_path = os.path.join(folder_path, file)
            image = load_image(img_path)
            
            if image:
                st.image(image, use_column_width=True)
                
                meta = get_metadata(file)
                
                # Title and details
                st.markdown(f"**{meta['title']}**")
                st.markdown(f"<div class='caption-text'>{meta['medium']}, {meta['year']}</div>", unsafe_allow_html=True)
                
                # Award if present
                if (meta['award']):
                    st.markdown(f"<div class='award-text'>🏆 {meta['award']}</div>", unsafe_allow_html=True)
                
                st.write("") # Spacer
                st.write("") # Spacer

# --- Navigation & Content ---

def main():
    st.sidebar.title("🎨 Art Portfolio")
    
    pages = {
        "🏠 Home / About Me": page_home,
        "🎨 Drawings & Paintings": lambda: page_gallery("🎨 Drawings & Paintings", "1.Paintings/"),
        "🦢 Origami": lambda: page_gallery("🦢 Origami Architecture", "2.Origami/"),
        "👟 Custom Shoe Art": lambda: page_gallery("👟 Custom Shoe Art", "3.Custom Shoe Art/"),
        "🤝 Community & Leadership": lambda: page_community("🤝 Community & Leadership", "4.Community Leadership/"),
        "🏆 Awards & Recognition": page_awards,
    }
    
    selection = st.sidebar.radio("Go to", list(pages.keys()))
    
    st.sidebar.markdown("---")
    
    st.sidebar.markdown("### 🔧 3D Printing Design")
    st.sidebar.info("[**View 3D Printing Showcase**](https://3d-printing-showcase.streamlit.app/)")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Contact")
    st.sidebar.info(
        """
        **Email:** student@example.com
        """
    )

    # Run the selected page function
    pages[selection]()

# --- Page Functions ---

def page_home():
    st.title("Welcome to My Creative Portfolio")
    
    # Use gap="large" for better visual separation
    col1, col2 = st.columns([1, 3], gap="large")
    
    with col1:
        # Looking for a profile pic in 0.About Me
        about_folder = "0.About Me/"
        profile_pic = None
        if os.path.exists(about_folder):
             files = [f for f in os.listdir(about_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.heic'))]
             if files:
                 profile_pic = os.path.join(about_folder, files[0])
        
        if profile_pic:
            st.image(profile_pic, caption="Tyler Liao", use_column_width=True)
        else:
            # Fallback if no profile pic
            hero_path = "1.Paintings/17BEDBFE-5596-4AEA-8B35-24C40735AFF2_1_105_c.jpeg"
            if os.path.exists(hero_path):
                st.image(hero_path, use_column_width=True, caption="featured work: Quiet Reflection")

    with col2:
        st.markdown("""
        ### Hi, I’m Tyler Liao. 
        
        While I’m currently in 9th grade with an interest in mechanical engineering and STEM, art has been a lifelong passion. I started painting at age nine while camping, capturing the landscapes, shapes, and moments that stayed in my memory. Over the years, I’ve explored origami, custom shoe designs, and other creative projects that challenge me to think about structure, form, and detail.

        **Why Art Matters to Me**
        
        Art isn’t just a hobby—it’s shaped :blue[how I observe the world, approach problems, and connect with others.] In high school, I shared this passion with my community by leading art festivals and teaching children how to create and express themselves.

        This portfolio showcases my journey, from personal experimentation to community engagement, highlighting how creativity and engineering intersect in my life.
        """)

    st.markdown("---")
    
    st.subheader("My Creative Journey & Philosophy")
    st.markdown("I have always been fascinated by how things are put together. From an early age, I found myself drawn to both the fluidity of paint and the precision of paper folding.")
    
    # Create two columns for the philosophy section to utilize the wide layout better
    phil_col1, phil_col2 = st.columns(2, gap="large")
    
    with phil_col1:
        st.markdown("""
        <div class="philosophy-box">
            <h4>Intersection of Engineering & Art</h4>
            <p>My work often explores the intersection of organic forms and geometric structures. In my paintings, I try to capture the quiet moments of observation. In my origami, I challenge myself to transform a single flat sheet into complex, 3D sculptures without cutting or gluing.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with phil_col2:
        st.markdown("""
        <div class="philosophy-box">
            <h4>Leadership & Community</h4>
            <p>Leadership in the arts is important to me. Organizing local workshops has taught me that art is a universal language that can bridge gaps in our community.</p>
        </div>
        """, unsafe_allow_html=True)

def page_gallery(title, folder):
    st.title(title)
    st.markdown("---")
    display_gallery(folder)

def page_community(title, folder):
    st.title(title)
    st.markdown("""
    Art is not just a solitary pursuit; it is a way to connect. 
    I believe in using creativity as a tool for leadership and community building.
    Below are some of the initiatives I've been proud to be a part of.
    """)
    st.markdown("---")
    display_gallery(folder, col_width=2) # Wider columns for community photos

def page_awards():
    st.title("🏆 Awards & Recognition")
    st.markdown("A summary of distinctions received for artistic excellence and community contributions.")
    st.markdown("---")
    
    for award in AWARDS_LIST:
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"**{award['year']}**")
            with col2:
                st.markdown(f"**{award['title']}**")
                st.caption(award['description'])
            st.divider()

if __name__ == "__main__":
    main()
