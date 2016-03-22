# we need a table to store products
db.define_table('product',
   Field('name',notnull=True,unique=True),
   Field('price','double',requires=IS_NOT_EMPTY()),
   Field('description','text',requires=IS_NOT_EMPTY()),
   Field('image','upload',requires=IS_NOT_EMPTY()),
   Field('sortable',requires=IS_IN_SET(['Clothings','Accessories','None'])),
   Field('Gender',requires=IS_IN_SET(['Male','Female','None'])),#1=men 2=women 3=none
   Field('Typecloth',requires=IS_IN_SET(['Topwear','Bottomwear','None'])),#1=top 2=bottom 3=none
   Field('Typeacc',requires=IS_IN_SET(['Laptop','Mobile','None'])),#1=laptops 2=phones 3=none
   auth.signature,
   format='%(name)s')

# and one table to store sales of products to users
db.define_table('sale',
   Field('invoice'),
   Field('creditcard'),             
   Field('buyer',db.auth_user),
   Field('product',db.product),
   Field('quantity','integer'),
   Field('price','double'),
   Field('shipped','boolean',default=False),
   Field('shipping_address'),
   Field('shipping_city'),
   Field('shipping_state'),
   Field('shipping_zip_code'),
   Field('shipping_date','datetime'),
   Field('delivery_date','datetime'),
   Field('tracking_number'),
   auth.signature)
db.define_table('wallpapers',
               Field('number','integer',requires=IS_NOT_EMPTY()),
               Field('image','upload'))
# we also make session cart, just in case
session.cart = session.cart or {}
