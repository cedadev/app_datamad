$('.visibility').on('click',function(e){
    // Toggle the icon and make the change in the database
    e.preventDefault();
    const url = e.currentTarget.href
    $.get(url)
    $(e.target).toggleClass("fa-eye fa-eye-slash")
})