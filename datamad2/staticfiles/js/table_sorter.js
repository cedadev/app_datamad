function display_hidden_facets(event, el, prefix, facet) {
    let hidden = $(el + '[id='+ prefix + facet + ']')
    hidden.toggleClass('d-none')

    let e = $(event)
    let message = e.attr('data-label')
    if (e.html() === message ){
        e.html("Hide")
    } else {
        e.html(message)
    }
}

function trigger_submit(element){
    $(element).trigger('submit')
}

$('#search_form').submit(function(event){
    // Stop the default form submission
    event.preventDefault();

    // Extract the values from the form and the current URL
    let form_qs = $('#search_form').serialize()
    let formParams = new URLSearchParams(form_qs)
    let urlParams = new URLSearchParams(window.location.search)

    // Add the form values to the current URL

    // clean the url from the show_hidden param
    // to allow it to be set from the form as
    // jQuery.serialize() does not serialise
    // radio or checkbox inputs unless they are checked
    urlParams.delete('show_hidden')

    for (const param of formParams.entries()) {
        // Clean the url of fields contained in the form
        urlParams.delete(param[0])

        // If the form contains a value, set the url field
        if (param[1] !== "") {
            urlParams.set(...param)
        }
    }

    // Delete the page param as we are starting a new search
    if (urlParams.has('page')){
        urlParams.delete('page')
    }

    // Handle adding the search character
    let new_qs = urlParams.toString();
    if (new_qs) {
        new_qs = '?' + new_qs
    }

    // Reload page with changes
    window.location.href = window.location.origin + new_qs;

})

$('.clear-facets').click(function (event) {
    event.preventDefault();
    let facet = $(this).attr('data-facet')
    let urlParams = new URLSearchParams(window.location.search)
    let selectedFacets = urlParams.getAll('selected_facets')

    // Search to see if the facet is in the list
    let findex = -1;
    for (let i = 0; i < selectedFacets.length; i++) {
        if (selectedFacets[i].startsWith(facet)) {
            findex = i;
            break;
        }
    }

    // Delete the facet
    if (findex > -1) {
        selectedFacets.splice(findex, 1);
    }

    // Delete all selected facets
    urlParams.delete('selected_facets')

    // Re-add any remaining facets
    selectedFacets.forEach(function (facet) {
        urlParams.append('selected_facets', facet)
    })

    // Handle adding the search character
    let new_qs = urlParams.toString();
    if (new_qs) {
        new_qs = '?' + new_qs
    }

    // Reload page with changes
    window.location.href = window.location.origin + new_qs;

})


$(function () {
    $('[data-toggle="tooltip"]').tooltip();
})


$(".claim-btn").click(function () {
    let btn = $(this);
    let url = 'grant/' + $(this).attr('data-id') + '/change_claim/';
    let datacentre = $(this).attr('data-dc');
    let csrftoken = getCookie('csrftoken')
    let cell = btn.parent();

    $.ajax({
        headers: {
            'X-CSRFToken': csrftoken
        },
        type: "POST",
        url: url,
        data: {'assigned_data_centre': datacentre},

        // handle a successful response
        success: function () {
            cell.html("CLAIMED");
            cell.attr('id', 'claim');
        },
        // handle a non-successful response
        error: function () {
            alert('There was an error claiming the grant');
        }
    });
});

