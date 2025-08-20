// Konfigurasi Firebase Anda
// Ganti nilai-nilai berikut dengan konfigurasi dari konsol Firebase Anda
// Anda bisa menemukannya di: Project settings > Your apps
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_AUTH_DOMAIN",
    databaseURL: "YOUR_DATABASE_URL",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_STORAGE_BUCKET",
    messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
    appId: "YOUR_APP_ID"
};

// Inisialisasi Firebase
firebase.initializeApp(firebaseConfig);
const database = firebase.database();

// Dapatkan referensi ke elemen HTML
const suhuEl = document.getElementById('suhu-value');
const humEl = document.getElementById('hum-value');
const preEl = document.getElementById('pre-value');
const wetEl = document.getElementById('wet-value');
const fuzzEl = document.getElementById('fuzz-value');
const statusEl = document.getElementById('status-message');

// Tentukan path ke data Anda di Firebase.
// Ganti "YOUR_USER_ID" dengan id yang digunakan di skrip Python
const dataRef = database.ref('YOUR_USER_ID');

// Dengarkan perubahan data di Firebase
dataRef.on('value', (snapshot) => {
    const data = snapshot.val();
    if (data) {
        // Perbarui UI dengan data terbaru
        suhuEl.textContent = data.tmp || '--';
        humEl.textContent = data.hum || '--';
        preEl.textContent = data.pre || '--';
        wetEl.textContent = data.wet || '--';
        fuzzEl.textContent = data.fuzz || '--';
        statusEl.textContent = `Data terakhir diperbarui: ${new Date().toLocaleTimeString()}`;
        statusEl.classList.remove('loading');
    } else {
        statusEl.textContent = 'Tidak ada data ditemukan.';
        statusEl.classList.remove('loading');
    }
}, (error) => {
    // Tangani kesalahan
    console.error("Gagal membaca data dari Firebase:", error);
    statusEl.textContent = 'Gagal memuat data. Periksa koneksi atau konfigurasi.';
    statusEl.classList.remove('loading');
});