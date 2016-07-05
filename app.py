import re,random, socket

class Server():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.routing = {'/' : self.index, '/index' : self.index, '404': self.page_not_found}

        self.connections = {}

        self.dictionary = {
            'positive': ['yes', 'yep', 'greetings', 'hi', 'hello', 'alloha', 'salam'],
            'negative': ['no', 'nope', 'not', 'bye'],
            'simple': ['It\'s interesting. Continue.', 'Want something else to talk?', 'You are funny'],
            'joke': ['I don\'t have a leg',
                     'I think you should go to doctor. You speak with computer!',
                     'Ohh new cookies',
                     'I work on cookies :)',
                     'Don\'t tell anyone, but i am a robot']
        }

        self.socket = socket.socket()
        self.socket.bind((host, port))

        self.socket.listen(5)
        self.listen()

    def listen(self):
        while True:
            connection, address = self.socket.accept()

            page, cookie = self.route(connection.recv(1024))

            id = random.randint(0, 10**20)
            connection.send(('HTTP/1.1 200 OK\nContent-Type: text/html\n{}\n')
                            .format(cookie)
                            .encode('utf-8'))
            connection.send("""{}"""
                            .format(page)
                            .encode('utf-8'))
            connection.close()

    def route(self, request):
        lines = request.decode('utf-8').split('\r\n')

        header = lines[0].split(' ')
        params = lines[len(lines)-1].split('&')

        cookie_id = ''
        identification_id = ''
        for line in lines:
            if 'Cookie' in line:
                cookie = re.split(': |;', line)
                for record in cookie:
                    if 'identification_id' in record:
                        identification_id = str(record.split('=')[1])
                        break

        if identification_id == '':
            cookie_id = 'Set-cookie: identification_id={}'.format(random.randint(0, 10**20))

        if identification_id not in self.connections.keys():
            self.connections[identification_id] = {'log': '', 'start': True}

        data = {}
        for param in params:
            arg = param.split('=')
            if len(arg) > 1:
                data[arg[0]] = arg[1]
        if header[1] in self.routing.keys():
            return self.routing[header[1]](header[0], data = data, identification_id = identification_id), cookie_id
        else:
            return self.routing['404'](), cookie_id

    def render_template(self, name, **args):
        page = open('templates/' + name).read()
        regular = re.compile('{{ \w* }}')
        static = regular.split(page)
        variables = regular.findall(page)

        result = ''
        for i in range(len(variables)):
            result += static[i] + args[variables[i].split(' ')[1]]
        result += static[len(static)-1]
        return result

    def index(self, method, data = {}, identification_id = ''):
        if method == 'GET':
            self.connections[identification_id]['log'] = '<p>Greetings, friend.</p><p> Do you want to speak with me? :)</p>'
            self.connections[identification_id]['start'] = True
        elif method == 'POST':
            data['text'] = self.parse_text(data['text'])
            if self.connections[identification_id]['start']:
                self.connections[identification_id]['log'] += self.first_dialog(data['text'])
                self.connections[identification_id]['start'] = False
            else:
                self.connections[identification_id]['log'] += self.continue_dialog(data['text'])

        return self.render_template('index.html', message = self.connections[identification_id]['log'])

    def first_dialog(self, text):
        dialog = '<p>User: {}</p>'.format(text)
        text = text.lower()
        positive, negative = False, False
        for accept in self.dictionary['positive']:
            if accept in text:
                positive = True
        for denial in self.dictionary['negative']:
            if denial in text:
                negative = True
        if (positive and negative) or (not positive and not negative):
            dialog += '<p>Sorry, I could not understand you</p>'
        elif positive:
            dialog += '<p>Very good. I like to speak with people.</p><p>Tell something about you.</p>'
        else:
            dialog += '<p>I am upset. But you could find me here at any moment :)</p>'
        return dialog

    def continue_dialog(self, text):
        dialog = '<p>User: {}</p>'.format(text)
        text = text.lower()
        if random.randint(0,100) > 50:
            dialog += '<p>{}</p>'.format(self.dictionary['joke'][random.randint(0, len(self.dictionary['joke'])-1)])
        dialog += '<p>{}</p>'.format(self.dictionary['simple'][random.randint(0,len(self.dictionary['simple'])-1)])
        return dialog

    def parse_text(self, text):
        symbols = {'2C': ',', '3A': ':', '3B' : ';', '28': '(', '29': ')', '21' : '!', '3F' : '?', '5C' : '\\', '2F' : '/',
                   '2B': '+', '40': '@'}
        l = list(text)
        l = [' ' if s == '+' else s for s in l]
        i = 0
        while i < len(l):
            if l[i] == '%':
                l = l[0:i] + list(symbols[l[i+1] + l[i+2]]) + l[i+3:]
            i += 1
        return ''.join(l)

    def page_not_found(self):
        return self.render_template('404.html')

if __name__ == '__main__':
    server = Server('', 8000)
