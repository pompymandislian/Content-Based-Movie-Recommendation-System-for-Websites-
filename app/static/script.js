document.addEventListener("DOMContentLoaded", function() {
    // Event listener untuk form rekomendasi
    document.getElementById("recommend-form").addEventListener("submit", async function(event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        const movieName = formData.get("movie-name");
        const response = await fetch(`/recommend/?movie_name=${encodeURIComponent(movieName)}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
        });

        const data = await response.json();
        console.log(data);  // Make sure data success accepted in console browser

        // Create HTML for movies
        let moviesHTML = '';
        data.forEach(movie => {
            moviesHTML += ` <div class="prev"><i class="fas fa-chevron-left"></i></div>
                            <div class="next"><i class="fas fa-chevron-right"></i></div>
                            <div class="poster">
                            <img src="${movie.poster_url}" alt="${movie.title}" />
                            <div>
                            <p>${movie.title}</p>
                            </div>
                        </div>`;
        });
        // Tampilkan daftar film di elemen 'result'
        document.getElementById("result").innerHTML = moviesHTML;
    });

    // Event listener untuk navigasi kiri
    document.querySelector('.prev').addEventListener('click', function() {
        document.querySelector('.image-container').scrollLeft -= 300;
        document.querySelector('.poster').scrollLeft -= 300; 
    });

    // Event listener untuk navigasi kanan
    document.querySelector('.next').addEventListener('click', function() {
        document.querySelector('.image-container').scrollLeft += 300; 
        document.querySelector('.poster').scrollLeft += 300; 
    });
});
