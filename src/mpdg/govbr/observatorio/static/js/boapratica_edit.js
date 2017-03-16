$(function(){

    $('#formfield-form-widgets-uf').hide();

    $('#formfield-form-widgets-esfera input:radio').change(function(e){

        if (this.value == 'estadual') {
            $('#formfield-form-widgets-uf').show();
        } else {
            $('#formfield-form-widgets-uf').hide();
        }
        
    });
});