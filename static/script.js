
document.addEventListener('DOMContentLoaded', function() {

    // Disables Episode if Movie is Selected
    const select_type = document.getElementById("add_type");
    const season = document.getElementById("add_season");
    const episodes = document.getElementById("add_episode");

    if (select_type && season && episodes) {
        select_type.addEventListener("change", function() {
            if (select_type.value === "movie") {
                episodes.disabled = true;
                episodes.value = "1";

                season.disabled = true;
                season.value = "1";
            } else {
                episodes.disabled = false;
                season.disabled = false;
            }
        });
    }
    // Show and Disable Episode and Season Form
    const movie_select = document.getElementById("mv_name")
    const show_se = document.getElementById("series-fields")

    if (movie_select && show_se) {
        movie_select.addEventListener('change', function() {

            const selectedOption = this.options[this.selectedIndex];
            const type = selectedOption.getAttribute('data-type');

            if (type && type.toLowerCase() === "movie") {
                show_se.style.display = 'none';
            } else {
                show_se.style.display = 'block';
            }
        });
    }
    // Reset Form when Modal Closes
    const modals = document.querySelectorAll('.modal')

    modals.forEach(modal => {
        modal.addEventListener('hidden.bs.modal', function() {

            const form = modal.querySelector('form');

            if (form) {
                form.reset();
            }

            const movie_modal = modal.querySelector('#series-fields');
            if (movie_modal) {
                movie_modal.style.display = 'block';
            }

            const disable_field = modal.querySelectorAll('input[disabled], select[disabled]');
            disable_field.forEach(input => {
                input.disabled = false;
            });
        });
    });
});

