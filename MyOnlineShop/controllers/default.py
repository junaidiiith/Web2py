# list of products
def index():
    form=SQLFORM.factory(Field('search',requires=IS_NOT_EMPTY())).process()
    if form.accepts(request):
        keywords = form.vars.search.split()
        query = reduce(lambda a,b:a|b,[db.product.name.like('%'+key+'%') for key in keywords])
        products = db(query).select(orderby=db.product.price)
    else:
        products=None
    if products and len(products)==1:
        redirect(URL('show',args=products.first().id))
    p=db().select(db.wallpapers.ALL)
    return locals()
def clothings():
    clothes=db(db.product.sortable == 'Clothings').select()
    menu1=[['Men clothings',False,'menclothes',[['Topwear',False,'topmen'],['Bottomwear',False,'bottommen']]]]
    menu2=[['Women Clothings',False,'womenclothes',[['Topwear',False,'topwomen'],['Bottomwear',False,'bottomwomen']]]]
    return locals()
def accessories():
    acc=db(db.product.sortable == 'Accessories').select()
    menu1=[['Laptops',False,'laptopss']]
    menu2=[['Mobiles',False,'mobiless']]
    return locals()
def menclothes():
    men = db((db.product.sortable == 'Clothings') & (db.product.Gender == 'Male')).select()
    menu1=[['Topwear',False,'topmen']]
    menu2=[['Bottomwear',False,'bottommen']]
    return locals()
def womenclothes():
    women = db((db.product.sortable == 'Clothings') & (db.product.Gender == 'Female')).select()
    menu1=[['Topwear',False,'topwomen']]
    menu2=[['Bottomwear',False,'bottomwomen']]
    return locals()
def topmen():
    tmen = db((db.product.sortable == 'Clothings') & (db.product.Gender == 'Male') & (db.product.Typecloth == 'Topwear')).select()
    return locals()
def bottommen():
    bmen = db((db.product.sortable == 'Clothings') & (db.product.Gender == 'Male') & (db.product.Typecloth == 'Bottomwear')).select()
    return locals()
def topwomen():
    twomen = db((db.product.sortable == 'Clothings') & (db.product.Gender == 'Female') & (db.product.Typecloth == 'Topwear')).select()
    return locals()
def bottomwomen():
    bwomen = db((db.product.sortable == 'Clothings') & (db.product.Gender == 'Female') & (db.product.Typecloth == 'Bottomwear')).select()
    return locals()
def laptopss():
    laptops = db((db.product.sortable == 'Accessories') & (db.product.Typeacc == 'Laptop')).select()
    return locals()
def mobiless():
    mobiles = db((db.product.sortable == 'Accessories') & (db.product.Typeacc == 'Mobile')).select()
    return locals()
def show():
    p=db.product(request.args(0,cast=int))
    return dict(p=p)

# login, registration, etcetera
def user():
    return dict(form=auth())

# an action to download uploaded images
def download():
    return response.download(request,db)

# an action to expose web services
def call():
    session.forget()
    return service()


# an action to see and process a shopping cart
def cart():
    if not session.cart:
        session.flash = 'Add something to shopping cart'
        redirect(URL('index'))
    total = sum(db.product(id).price*qty for id,qty in session.cart.items())
    return dict(cart=session.cart,total=total)

# time to pay ... now for real
@auth.requires_login()
def buy():
    if not session.cart:
        session.flash = 'Add something to shopping cart'
        redirect(URL('index'))
    import uuid
    invoice = str(uuid.uuid4())
    total = sum(db.product(id).price*qty for id,qty in session.cart.items())
    form = SQLFORM.factory(
               Field('creditcard',default='4427802641004797',requires=IS_NOT_EMPTY()),
               Field('expiration',default='12/2012',requires=IS_MATCH('\d{2}/\d{4}')),
               Field('cvv',default='123',requires=IS_MATCH('\d{3}')),
               Field('shipping_address',requires=IS_NOT_EMPTY()),
               Field('shipping_city',requires=IS_NOT_EMPTY()),
               Field('shipping_state',requires=IS_NOT_EMPTY()),
               Field('shipping_zip_code',requires=IS_MATCH('\d{5}(\-\d{4})?')))
    if form.accepts(request,session):
        for key, value in session.cart.items():
            db.sale.insert(invoice=invoice,
                               buyer=auth.user.id,
                               product = key,
                               quantity = value,
                               price = db.product(key).price,
                               creditcard = form.vars.creditcard,
                               shipping_address = form.vars.shipping_address,
                               shipping_city = form.vars.shipping_city,
                               shipping_state = form.vars.shipping_state,
                               shipping_zip_code = form.vars.shipping_zip_code)
        session.cart.clear()
        session.flash = 'Thank you for your order'
        redirect(URL('invoice',args=invoice))
    else:
        response.flash = "Do your payment carefully"
    return dict(cart=session.cart,form=form,total=total)

@auth.requires_login()
def invoice():
    return dict(invoice=request.args(0))

# an action to add and remove items from the shopping cart
def cart_callback():
    id = int(request.vars.id)
    if request.vars.action == 'add':
        session.cart[id]=session.cart.get(id,0)+1
        if request.vars.url == 'cart':
            redirect(request.vars.url)
        else:
            redirect(URL(request.vars.url,args=id))
    if request.vars.action == 'sub':
        session.cart[id]=max(0,session.cart.get(id,0)-1)
        redirect(URL(request.vars.url))
    return str(session.cart[id])

@auth.requires_login()
def myorders():
    orders = db(db.sale.buyer==auth.user.id).select(orderby=~db.sale.created_on)
    form=SQLFORM.factory(
                        Field('Invoice_code'))
    if form.accepts(request,session):
        db((db.sale.buyer==auth.user.id) & (db.sale.invoice==form.vars.Invoice_code)).delete()
        redirect(URL('myorders'))
    return dict(orders=orders,form=form)

@auth.requires_membership('manager')
def products():
    grid=SQLFORM.grid(db.product)
    return locals()
@auth.requires_membership('manager')
def edit_product():
    form = crud.update(db.product,request.args(0))
    return dict(form=form)
@auth.requires_membership('manager')
def users():
    db.auth_user.id.represent=lambda id:A('info',_href=URL('info_user',args=id))
    form,items = crud.search(db.auth_user)
    return dict(form=form,users=items)

@auth.requires_membership('manager')
def info_user():
    form = crud.read(db.auth_user,request.args(0))
    orders = db(db.sale.buyer==request.args(0)).select(orderby=~db.sale.created_on)
    return dict(form=form,orders=orders)

@auth.requires_membership('manager')
def edit_order():
    db.sale.invoice.writable=False
    db.sale.buyer.writable=False
    db.sale.creditcard.writable=False
    db.sale.product.writable=False
    form = crud.update(db.sale,request.args(0))
    return dict(form=form)
