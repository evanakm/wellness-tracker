def CreateTable(data):
    res = '<table class="table table-bordered"> \
        <thead> \
        <tr> \
        <th scope="col">#</th> \
        <th scope="col">Date</th> \
        <th scope="col">0</th> \
        <th scope="col">1</th> \
        <th scope="col">2</th> \
        <th scope="col">3</th> \
        <th scope="col">4</th> \
        <th scope="col">5</th> \
        <th scope="col">6</th> \
        <th scope="col">7</th> \
        <th scope="col">8</th> \
        <th scope="col">9</th> \
        <th scope="col">10</th> \
        <th scope="col">11</th> \
        <th scope="col">12</th> \
        <th scope="col">13</th> \
        <th scope="col">14</th> \
        <th scope="col">15</th> \
        <th scope="col">16</th> \
        <th scope="col">17</th> \
        <th scope="col">18</th> \
        <th scope="col">19</th> \
        <th scope="col">20</th> \
        <th scope="col">21</th> \
        <th scope="col">22</th> \
        <th scope="col">23</th> \
        </tr> \
        </thead> \
        <tbody>'

    for i in range(len(data)):
        res = res + \
        '<tr> \
        <th scope="row">' + data[i]['date'] + '</th>' + \
        '<td>' + data[i]['hours']['00'] +'</td>' + \
        '<td>' + data[i]['hours']['01'] +'</td>' + \
        '<td>' + data[i]['hours']['02'] +'</td>' + \
        '<td>' + data[i]['hours']['03'] +'</td>' + \
        '<td>' + data[i]['hours']['04'] +'</td>' + \
        '<td>' + data[i]['hours']['05'] +'</td>' + \
        '<td>' + data[i]['hours']['06'] +'</td>' + \
        '<td>' + data[i]['hours']['07'] +'</td>' + \
        '<td>' + data[i]['hours']['08'] +'</td>' + \
        '<td>' + data[i]['hours']['09'] +'</td>' + \
        '<td>' + data[i]['hours']['10'] +'</td>' + \
        '<td>' + data[i]['hours']['11'] +'</td>' + \
        '<td>' + data[i]['hours']['12'] +'</td>' + \
        '<td>' + data[i]['hours']['13'] +'</td>' + \
        '<td>' + data[i]['hours']['14'] +'</td>' + \
        '<td>' + data[i]['hours']['15'] +'</td>' + \
        '<td>' + data[i]['hours']['16'] +'</td>' + \
        '<td>' + data[i]['hours']['17'] +'</td>' + \
        '<td>' + data[i]['hours']['18'] +'</td>' + \
        '<td>' + data[i]['hours']['19'] +'</td>' + \
        '<td>' + data[i]['hours']['20'] +'</td>' + \
        '<td>' + data[i]['hours']['21'] +'</td>' + \
        '<td>' + data[i]['hours']['22'] +'</td>' + \
        '<td>' + data[i]['hours']['23'] +'</td>' + \
        '</tr>'

    res = res + '</tbody></table>'

    return res

