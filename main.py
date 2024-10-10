# Langkah 1: Instalasi Pustaka yang Diperlukan
# Jalankan perintah ini di terminal Anda untuk menginstal pustaka jika belum terinstal
# !pip install pandas nltk PyMuPDF streamlit

# Langkah 2: Mengimpor Pustaka
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
import fitz  # PyMuPDF
import streamlit as st
import re

st.set_page_config(
    page_title='KELOMPOK 4 SPK',
)

# Mengunduh stopwords dan tokenizer dari NLTK
nltk.download('punkt')
nltk.download('stopwords')

# Mengatur stopwords dalam bahasa Inggris
stop_words = set(stopwords.words('english'))

# Langkah 3: Membaca data dari file CSV
df_upwork_jobs = pd.read_csv('upwork-jobs.csv')

# Langkah 4: Mengunggah file PDF CV melalui Streamlit (dibatasi hanya 1 file)
uploaded_file = st.file_uploader("Unggah file CV Anda (format PDF)", type="pdf")

# Mengecek apakah ada file yang diunggah
if uploaded_file is not None:
    # Membaca file PDF yang diunggah menggunakan PyMuPDF
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    
    # Ekstraksi teks dari PDF CV
    cv_text = ""
    for page in doc:
        cv_text += page.get_text()

    st.write("Teks dari CV (500 karakter pertama):")
    st.text(cv_text[:500])  # Tampilkan 500 karakter pertama dari teks CV
    
    # Langkah 5: Preprocessing Teks CV
    def preprocess_text(text):
        # Tokenisasi teks
        tokens = word_tokenize(text.lower())
        # Hapus stopwords dan tanda baca
        tokens = [word for word in tokens if word not in stop_words and word not in string.punctuation]
        return tokens

    # Preprocessing teks dari CV
    cv_skills = preprocess_text(cv_text)

    # Langkah 6: Fungsi untuk mencocokkan keterampilan CV dengan deskripsi pekerjaan
    def match_skills(cv_skills, job_description):
        job_tokens = preprocess_text(job_description)  # Proses deskripsi pekerjaan
        matching_skills = set(cv_skills).intersection(set(job_tokens))
        return len(matching_skills), matching_skills  # Mengembalikan jumlah dan keterampilan yang cocok

    # Langkah 7: Terapkan fungsi pencocokan pada dataset pekerjaan dengan progress bar
    st.write("Mencocokkan pekerjaan... Harap tunggu.")
    progress_bar = st.progress(0)  # Membuat progress bar
    total_jobs = len(df_upwork_jobs)  # Menghitung jumlah total pekerjaan
    step = 100 // total_jobs  # Membagi progress bar berdasarkan jumlah pekerjaan

    matches = []
    for index, row in df_upwork_jobs.iterrows():
        match_result = match_skills(cv_skills, row['description'])  # Pencocokan keterampilan
        matches.append(match_result)

        # Update progress bar
        progress = (index + 1) * step
        progress_bar.progress(min(progress, 100))  # Progress tidak boleh lebih dari 100

    # Tambahkan hasil pencocokan ke dalam DataFrame
    df_upwork_jobs['matches'] = matches

    # Pisahkan 'matches' menjadi dua kolom: 'num_matches' dan 'matching_skills'
    df_upwork_jobs['num_matches'] = df_upwork_jobs['matches'].apply(lambda x: x[0])  # Jumlah keterampilan yang cocok
    df_upwork_jobs['matching_skills'] = df_upwork_jobs['matches'].apply(lambda x: list(x[1]))  # Daftar keterampilan yang cocok

    # Drop kolom 'matches' jika tidak diperlukan lagi
    df_upwork_jobs = df_upwork_jobs.drop(columns=['matches'])

    # Langkah 8: Tambahkan preprocessing untuk membersihkan judul pekerjaan
    def clean_title(title):
        # Buat list kata yang tidak relevan untuk dihapus dari judul
        irrelevant_words = ['remote', 'terpencil', 'indonesia', 'contract', 'freelance', 'part-time', 'full-time','Looking for','Saat ini kami sedang']
        
        # Tokenisasi judul
        title_tokens = word_tokenize(title.lower())
        
        # Hapus kata-kata yang tidak relevan
        cleaned_tokens = [word for word in title_tokens if word not in irrelevant_words]
        
        # Gabungkan kembali token menjadi string
        cleaned_title = ' '.join(cleaned_tokens)
        
        # Hapus tanda baca yang tidak relevan
        cleaned_title = re.sub(r'[^\w\s]', '', cleaned_title)
        
        return cleaned_title

    # Bersihkan title sebelum mencocokkan kategori
    df_upwork_jobs['cleaned_title'] = df_upwork_jobs['title'].apply(clean_title)

    def categorize_job(title):
        title_lower = title.lower()

        # Kategori developer
        if 'full stack developer' in title_lower:
            return 'full stack developer'
        elif 'frontend developer' in title_lower or 'front end developer' in title_lower:
            return 'frontend developer'
        elif 'backend developer' in title_lower or 'back end developer' in title_lower:
            return 'backend developer'
        elif 'mobile developer' in title_lower or 'ios developer' in title_lower or 'android developer' in title_lower:
            return 'mobile developer'
        elif 'web developer' in title_lower:
            return 'web developer'
        elif 'software developer' in title_lower or 'software engineer' in title_lower:
            return 'software developer'

        # Kategori UI/UX dan Desain
        elif 'ui/ux designer' in title_lower or 'ui designer' in title_lower or 'ux designer' in title_lower:
            return 'ui ux designer'
        elif 'graphic designer' in title_lower:
            return 'graphic designer'
        elif 'product designer' in title_lower:
            return 'droduct designer'

        # Kategori engineer
        elif 'engineer' in title_lower:
            return 'engineer'
        elif 'devops' in title_lower or 'site reliability engineer' in title_lower:
            return 'devOps engineer'
        elif 'data engineer' in title_lower:
            return 'data engineer'
        elif 'machine learning engineer' in title_lower:
            return 'machine learning engineer'

        # Kategori data
        elif 'data scientist' in title_lower:
            return 'data scientist'
        elif 'data analyst' in title_lower:
            return 'data analyst'
        elif 'business analyst' in title_lower:
            return 'business analyst'

        # Kategori marketing
        elif 'marketing' in title_lower:
            return 'marketing'
        elif 'digital marketing' in title_lower:
            return 'digital marketing'
        elif 'content writer' in title_lower or 'copywriter' in title_lower:
            return 'content writer'
        elif 'seo specialist' in title_lower:
            return 'SEO specialist'
        elif 'social media manager' in title_lower:
            return 'social media'

        # Kategori project management dan lainnya
        elif 'project manager' in title_lower or 'product manager' in title_lower:
            return 'project manager'
        elif 'qa engineer' in title_lower or 'quality assurance' in title_lower:
            return 'qa'
        elif 'system administrator' in title_lower or 'sysadmin' in title_lower:
            return 'system administrator'
        elif 'it support' in title_lower:
            return 'it support'

        # Jika tidak ada kecocokan, masukkan ke dalam kategori 'Other'
        else:
            return 'other'

    # Terapkan fungsi kategorisasi ke kolom 'title'
    df_upwork_jobs['category'] = df_upwork_jobs['title'].apply(categorize_job)

    # Langkah 9: Urutkan pekerjaan berdasarkan kecocokan keterampilan tertinggi
    recommended_jobs = df_upwork_jobs.sort_values(by='num_matches', ascending=False)

    # Langkah 10: Mengelompokkan pekerjaan berdasarkan kategori
    grouped_jobs = recommended_jobs.groupby('category')

    # Menampilkan link pekerjaan dan keterampilan yang cocok
    st.write("Pekerjaan dengan Kecocokan Keterampilan Tertinggi:")
    st.dataframe(recommended_jobs[['title']].head(20).reset_index(drop=True))

    # Langkah 11: Membaca data dari file CSV 'available_jobs.csv'
    df_available_jobs = pd.read_csv('available_jobs.csv')

    # Langkah 12: Menampilkan lowongan yang sesuai dengan kategori pekerjaan yang cocok
    st.write("Lowongan untuk kategori pekerjaan yang cocok:")
    matched_categories = recommended_jobs['category'].unique()

    for index, row in df_available_jobs.iterrows():
        # Cek apakah kategori pekerjaan di highest_matched_jobs ada di df_available_jobs
        if row['category'].lower() in matched_categories:
            st.write(f"- [{row['company']}]({row['link']}) untuk kategori **{row['category']}**")

    # Selesai, progress bar 100%
    progress_bar.progress(100)
else:
    st.write("Silakan unggah file CV Anda terlebih dahulu.")
