from System.Windows.Threading import DispatcherTimer
from System.Windows.Browser.HtmlPage import Document
from System import TimeSpan,Exception
import re

def calcgcd(a, b):
    x = max(a, b)
    y = min(a, b)
    while y > 1:
        m = x % y
        if m == 0: return y
        x, y = y, m
    return 1

class frac:
    def __init__(self, val):
        if val is None:
            n, d = 0, 1
        elif isinstance(val, list):
            n, d = val
        else:
            val = str(val)
            if val.find(' ') >= 0:
                wstr, fstr = val.split(' ', 1)
                w = int(wstr)
                f = frac(fstr)
                n = f.n + abs(w) * f.d
                if w < 0: n = -n
                d = f.d
            elif val.find('/') >= 0:
                nstr, dstr = val.split('/', 1)
                n, d = int(nstr), int(dstr)
            else:
                n, d = int(val), 1

        if d < 0: n, d = -n, -d
        gcd = calcgcd(d, abs(n))
        self.n, self.d = n/gcd, d/gcd

    def __repr__(self):
        if self.n == 0: return '0'
        if self.d == 1: return str(self.n)
        if abs(self.n) < self.d:  return '%d/%d' % (self.n, self.d)
        if self.n >= 0: return '%d %d/%d' % (self.n/self.d, self.n%self.d, self.d)
        return '-%d %d/%d' % (-self.n/self.d, -self.n%self.d, self.d)

    def __add__(self, other):
        if not isinstance(other, frac): other = frac(other)
        return frac([self.n * other.d + other.n * self.d, self.d * other.d])

    def __sub__(self, other):
        if not isinstance(other, frac): other = frac(other)
        return frac([self.n * other.d - other.n * self.d, self.d * other.d])

    def __mul__(self, other):
        if not isinstance(other, frac): other = frac(other)
        return frac([self.n * other.n, self.d * other.d])

    def __div__(self, other):
        if not isinstance(other, frac): other = frac(other)
        return frac([self.n * other.d, self.d * other.n])

    def __truediv__(self, other):
        return self.__div__(other)
        
    def __neg__(self):
        return frac([-self.n, self.d])

    def __abs__(self):
        return frac([abs(self.n), self.d])

    def __pos__(self):
        return frac([self.n, self.d])

    def __float__(self):
        return float(self.n) / float(self.d)

class fracexpr:
    frp = re.compile(r'(?:(?P<w>\d+)[.](?P<adp>\d+))|(?:(?P<w>\d+)\s+(?P<n>\d+)/(?P<d>\d+))|(?:(?P<n>\d+)/(?P<d>\d+))|(?P<w>\d+)')

    def __init__(self, text):
        self.text = text
        self.__evaltext = None
        self.__htmltext = None
           
    def evaltext(self):
        if self.__evaltext is None:
            def subeval(m):
                def gtoi(m, g):
                    v = m.group(g)
                    if v is None: return 0
                    else: return int(v)
                w = gtoi(m, 'w')
                adp = m.group('adp')    
                if adp is not None:  # special case for decimals
                    n, d = int(adp), pow(10, len(adp))
                else: # normal fraction
                    n, d = gtoi(m, 'n'), gtoi(m, 'd')
                if n == 0: return 'frac([%d,1])' % w
                else: return 'frac([%d,%d])' % (w*d+n, d)
            self.__evaltext = fracexpr.frp.sub(subeval, self.text)
        return self.__evaltext
    
    def eval(self):
        t = self.evaltext().strip()
        if t == '': return None
        return eval(t)
            
    def html(self):
        if self.__htmltext is None:
            l = fracexpr.frp.split(self.text)
            i = 0
            s = '<table><tr>\n'
            c = True
            repl = [
                ('/', '&nbsp;&#247;&nbsp;'),
                ('*', '&nbsp;&#215;&nbsp;'),
                ('+', '&nbsp;+&nbsp;'),
                ('-', '&nbsp;&#8722;&nbsp;'),
                ]
            while i < len(l):
                if c:
                    x = l[i]
                    for cf, cr in repl: x = x.Replace(cf, cr)
                    s += '<td class="op">%s</td>' % x
                    i += 1
                else:
                    w, adp, n, d = l[i], l[i+1], l[i+2], l[i+3]
                    if adp is not None:
                        s += '<td class="wp">%s.%s</td>' % (w, adp)
                    else:
                        if w is not None:
                            s += '<td class="wp">%s</td>' % w
                        if n is not None:
                            s += '<td class="fp">%s<hr class="fr" />%s</td>' % (n,d)
                    i += 4
                c = not c
            s += '</tr></table>\n'
            self.__htmltext = s
        return self.__htmltext

def Refract(sender, e):
    global oldText
    newText = Document.input.value
    if newText is None: newText = ''
    else: newText = newText.strip()

    if newText == oldText: return

    e = fracexpr(newText)
    Document.evalExpression.innerHTML= e.evaltext()
    Document.formattedExpression.innerHTML = e.html()

    try:
        r = e.eval()
        
        if r is None:
            r = ''
        elif not isinstance(r, frac):
            raise Exception('Unexpected result type.')
            
        Document.result.innerHTML = fracexpr(str(r)).html()
        Document.evalException.innerHTML = 'None'
    except Exception, exp:
        Document.result.innerHTML = 'n/a' 
        Document.evalException.innerHTML = exp.Message
        
    oldText = newText
    
oldText = ''
t = DispatcherTimer()
t.Interval = TimeSpan.FromSeconds(0.5)
t.Tick += Refract
t.Start()

