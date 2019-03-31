$(document).ready(function() {

    Webcam.set({
			width: 400,
			height: 300,
			image_format: 'jpeg',
			jpeg_quality: 90
    });
    Webcam.attach( '#my_camera' );

    function take_snapshot_for_text() {
        // take snapshot and get image data
        Webcam.snap( function(data_uri) {
            // display results in page
//            document.getElementById('results').innerHTML =
//                '<h2>Here is your image:</h2>' +
//                '<img src="'+data_uri+'"/>';
//            console.log(data_uri);


            $.ajax({
                type: "GET",
                url: $SCRIPT_ROOT + '/text',
                data: {"data_uri": data_uri},
//                dataType: 'json',
                success: function(data) {
                    var data_ = data.split('@');
                    $('.result_img').attr("src", "data:image/png;base64," + data_[0]);
                    $(".translation_english").text(data_[1]);
                },
                error: function(request, status, error){
                    console.log(error)
                    alert("No text detected! Please try again!")
                }
            });
        })
    }

    function take_snapshot_for_object() {
        // take snapshot and get image data
        Webcam.snap( function(data_uri) {

            $.ajax({
                type: "GET",
                url: $SCRIPT_ROOT + '/object',
                data: {"data_uri": data_uri},
                success: function(data) {
                    var data_ = data.split('@');
                    $('.result_img').attr("src", "data:image/png;base64," + data_[0]);
                    $(".translation_english").text(data_[1]);
                },
                error: function(request, status, error){
                    console.log(error)
                }
            });
        })
    }

    var history_table = $('table#history_table').DataTable({
            'responsive': true,
            "autoWidth": true,
            dom: 'Bfrtip',
//            buttons: [
//                'copy', 'csv', 'excel', 'pdf', 'print'
//            ],
            columns:
            [
                {
                    title: "Word",
                    data: 0,
                },
                {
                    title: "Translation",
                    data: 1
                }
            ]
        });

    // Language options
    var isoCountries = [
        { id: 'zh', text: 'Chinese', cty: "CN"},
        { id: 'ja', text: 'Japanese', cty: "JP"},
        { id: 'es', text: 'Spanish', cty: "ES"},
        { id: 'fr', text: 'French', cty: "FR"},
        { id: 'ko', text: 'Korean', cty: "KR"},
    ]
    // Get flash for each country
    function formatCountry (country) {
        if (!country.cty) { return country.text; }
        var $country = $(
        '<span class="flag-icon flag-icon-'+ country.cty.toLowerCase() +' flag-icon"></span>' +
        '<span class="flag-text">'+ country.text+"</span>"
        );
        return $country;
    };

    // Select language option
    var s2 = $(".languages").select2({
        templateResult: formatCountry,
        data: isoCountries
    });

    // Select all options as default
    var selectedItems = [];
    var allOptions = $(".languages option");
    allOptions.each(function() {
        selectedItems.push( $(this).val() );
    });
    s2.val(selectedItems).trigger("change");



     $("#text_recog").bind('click', function() {
        $(".translate-output").show()
        take_snapshot_for_text();
    });

    $("#object_detect").bind('click', function() {
        $(".translate-output").show()
        take_snapshot_for_object();
    })


    $('p.translation_english').bind("DOMSubtreeModified",function(){
        var word = $(this).text();
        var langs = $('.languages').val();
        translation(word, langs)
//        console.log(langs);
    });


    var CountriesDict = {
        'zh': 'Chinese',
        'ja': 'Japanese',
        'es': 'Spanish',
        'fr': 'French',
        'ko': 'Korean'
    }

    var CountriesVoice = {
        'english': 'en-US',
        'zh': 'zh-CN',
        'ja': 'ja-JP',
        'es': 'es-ES',
        'fr': 'fr-FR',
        'ko': 'ko-KR'
    }

    function translation(word, langs){
        var base_url = "https://translate.yandex.net/api/v1.5/tr.json/translate?"
        var key = 'key=' + "API-KEY"
        var text = "text=" + word

        var requests = [];
        $.each(langs, function(index, lang) {
            requests.push(get_translated_data(word, lang))
        })
        $.when.apply($,requests).done(function(){
            var total = [];
            $.each(arguments, function (i, data) {
                total.push(data[0]['text']); //if the result of the ajax request is a int value then
                var lang = data[0]['lang'].split('-')[1];
                $(".translation_" + lang).text(data[0]['text']);
            });
//            console.log(total)
            history_table.row.add([word, total.join(", ")]).draw();
        })
    }


    function get_translated_data(word, lang) {
        var base_url = "https://translate.yandex.net/api/v1.5/tr.json/translate?"
        var key = 'key=' + "API-KEY"
        var text = "text=" + word
        var lang_str = "lang=en-" + lang
        var url = base_url + key + "&" + text + "&" + lang_str
        return $.ajax({
                type: "GET",
                dataType: 'json',
                url: url
        });
    }



    // Word pronunciation
    $('a.audio').click(function() {
        var item_id = $(this).attr('id')
        var lang = item_id.split('_')[2];

        var text = $(".translation_" + lang).text();
        var lang_code = CountriesVoice[lang]

        var msg = new SpeechSynthesisUtterance(text);
        msg.voice = speechSynthesis.getVoices().filter(function(voice) { return voice.lang == lang_code; })[0];
        speechSynthesis.speak(msg);
    })



//        $.ajax({
//            type: "GET",
//            url: url,
//            dataType: 'json',
//            complete : function(){
//            },
//            success: function(data){
//                translated_word = data['text'][0];
//                $(".translation_ch").text(translated_word);
//
//            }
//        });





    // Get translation



//    $('#form').on('submit', function(e){
///
})

