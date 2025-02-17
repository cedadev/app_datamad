
$(".claim-btn").click(function (event) {

    // Set needed variables
    let btn_value;
    let csrftoken = getCookie('csrftoken')

    const claim_key = "claimed";

    // Get values from the data attributes on the button
    var claimed = event.target.classList.contains(claim_key);
    let id = event.target.dataset.id;
    let datacentre = event.target.dataset.dc;
    let data = {};

    // Prepare values for the URL and button after the fact
    if (claimed) {
        // We are removing our claim so setting the datacentre to None
        btn_value = 'Claim';

    } else {
        // We are making a claim so the datacentre is set to the users
        btn_value = 'Unclaim';
        data.assigned_data_centre = datacentre
    }

    $.ajax({
        headers: {
            'X-CSRFToken': csrftoken
        },
        type: "POST",
        url: ['/grant', id, 'change_claim/'].join('/'),
        data: data,

        // handle a successful response
        success: function () {
            event.target.innerHTML = btn_value;

            if (claimed){
                event.target.classList.remove(claim_key);
            } else {
                event.target.classList.add(claim_key);
            }
        },
        // handle a non-successful response
        error: function (data) {
            if (data.status === 403){
                alert('You do not have permission to change the assigned data centre on this grant.')
            } else {
                alert('There was a problem changing the assigned data centre on this grant.')
            }
        }
    });
});


$(document).on('click', '.confirm', function(){
    return confirm('Are you sure you want to make this change?');
})