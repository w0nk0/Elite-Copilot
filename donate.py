
html="""
<!doctype html>
<html lang="en">
<head>

<style>
/*
 * -- BASE STYLES --
 * Most of these are inherited from Base, but I want to change a few.
 */
body {
    color: #826066;
}

h2, h3 {
    letter-spacing: 0.25em;
    text-transform: uppercase;
    font-weight: 600;
}

p {
    line-height: 1.3em;
}


/*
 * -- Layout Styles --
 */
.l-content {
    margin: 0 auto;
}

.l-box {
    padding: 0.5em 2em;
}

/*
 * -- MENU STYLES --
 * Make the menu have a very faint box-shadow.
 */
.pure-menu {
    box-shadow: 0 1px 1px rgba(0,0,0, 0.10);
}


/*
 * -- BANNER --
 * The top banner with the headings. By using a combination
 * of `display: table;` and `display: table-cell;`, we can
 * vertically center the text.
 */

.banner {
    background: transparent url('http://upload.wikimedia.org/wikipedia/commons/thumb/1/15/An_Infrared_View_of_the_Galaxy.jpg/1024px-An_Infrared_View_of_the_Galaxy.jpg') 0 0 no-repeat fixed;
    text-align: center;
    background-size: cover;
    filter: progid:DXImageTransform.Microsoft.AlphaImageLoader(src='http://upload.wikimedia.org/wikipedia/commons/thumb/1/15/An_Infrared_View_of_the_Galaxy.jpg/1024px-An_Infrared_View_of_the_Galaxy.jpg', sizingMethod='scale');

    height: 100px;
    width: 100%;
    margin-bottom: 2em;
    display: table;
}

    .banner-head {
        display: table-cell;
        vertical-align: middle;
        margin-bottom: 0;
        font-size: 1.6 em;
        color: white;
        font-weight: 290;
        text-shadow: 0 2px 2px black;
    }



/*
 * -- PRICING TABLE WRAPPER --
 * This element wraps up all the pricing table elements
 */
 .pricing-tables,
 .information {
    max-width: 980px;
    margin: 0 auto;
 }
.pricing-tables {
    margin-bottom: 2.0125em;
    text-align: center;
}

/*
 * -- PRICING TABLE  --
 * Every pricing table has the .pricing-table class
 */
.pricing-table {
    border: 2px solid #ddd;
    margin: 0 0.5em 2em;
    padding: 0 0 2.4em;
}

/*
 * -- PRICING TABLE HEADER COLORS --
 * Choose a different color based on the type of pricing table.
 */
.pricing-table-free .pricing-table-header {
    background: #519251;
}

.pricing-table-biz .pricing-table-header {
    background: #2c4985;
}

/*
 * -- PRICING TABLE HEADER --
 * By default, a header is black/white, and has some styles for its <h2> name.
 */
.pricing-table-header {
    background: #111;
    color: #fff;
}
    .pricing-table-header h2 {
        margin: 0;
        padding-top: 1.3em;
        font-size: 1em;
        font-weight: normal;

    }


/*
 * -- PRICING TABLE PRICE --
 * Styles for the price and the corresponding <span>per month</span>
 */
.pricing-table-price {
    font-size: 4em;
    margin: 0.2em 0 0;
    font-weight: 800;
}
    .pricing-table-price span {
        display: block;
        text-transform: uppercase;
        font-size: 0.2em;
        padding-bottom: 1.62 em;
        font-weight: 300;
        color: rgba(255, 255, 255, 0.5);
        *color: #fff;
    }



/*
 * -- PRICING TABLE LIST --
 * Each pricing table has a <ul> which is denoted by the .pricing-table-list class
 */
.pricing-table-list {
    list-style-type: none;
    margin: 0;
    padding: 0;
    text-align: center;
}


/*
 * -- PRICING TABLE LIST ELEMENTS --
 * Styles for the individual list elements within each pricing table
 */
.pricing-table-list li {
    padding: 0.5em 0;
    background: #f7f7f7;
    border-bottom: 1px solid #e7e7e7;
}


/*
 * -- PRICING TABLE BUTTON --
 * Styles for the "Choose" button at the bottom of a pricing table.
 * This inherits from Pure Button.
 */
.button-choose {
    border: 1px solid #ccc;
    background: #fdd;
    color: #333;
    border-radius: 2em;
    font-weight: bold;
    position: relative;
    bottom: -1.5em;
}

.information-head {
    color: black;
    font-weight: 500;
}

.footer {
    background: #111;
    color: #888;
    text-align: center;
}
    .footer a {
        color: #ddd;
    }



/*
 * -- TABLET MEDIA QUERIES --
 * On tablets, we want to slightly adjust the size of the banner
 * text and add some vertical space between the various pricing tables
 */
@media(min-width: 767px) {

    .banner-head {
        font-size: 2em;
    }
    .pricing-table {
        margin-bottom: 0;
    }

}

/*
 * -- PHONE MEDIA QUERIES --
 * On phones, we want to reduce the height and font-size of the banner further
 */
@media (min-width: 480px) {
    .banner {
        height: 200px;
    }
    .banner-head {
        font-size: 2em;
    }
}

</style>

    <meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=0.9">

    <title>Donate</title>

    


<link rel="stylesheet" href="http://yui.yahooapis.com/pure//pure.css">



<!--[if lte IE 8]>
  
    <link rel="stylesheet" href="http://yui.yahooapis.com/pure//grids-responsive-old-ie.css">
  
<![endif]-->
<!--[if gt IE 8]><!-->
  
    <link rel="stylesheet" href="http://yui.yahooapis.com/pure//grids-responsive.css">
  
<!--<![endif]-->



  
    <!--[if lte IE 8]>
        <link rel="stylesheet" href="css/layouts/pricing-old-ie.css">
    <![endif]-->
    <!--[if gt IE 8]><!-->
        <link rel="stylesheet" href="css/layouts/pricing.css">
    <!--<![endif]-->
  

    

</head>
<body bgcolor="#221111">

<!--
<div class="pure-menu pure-menu-open pure-menu-horizontal">
    <a href="#" class="pure-menu-heading">Your Logo</a>
    <ul>
        <li><a href="#">Home</a></li>
        <li class="pure-menu-selected"><a href="#">Pricing</a></li>
        <li><a href="#">Contact</a></li>
    </ul>
</div>
-->

<div class="banner">
    <h1 class="banner-head">
        This program is and will be free. <br>
		<br>
        Tips, however, are more than welcome.
    </h1>
</div>

<div class="l-content">
    <div class="pricing-tables pure-g">
        <div class="pure-u-1 pure-u-md-1-3">
            <div class="pricing-table pricing-table-enterprise">
                <div class="pricing-table-header">
                    <h2>Buy me an espresso!</h2>

                    <span class="pricing-table-price">
                        $3 <span></span>
                    </span>
                </div>

                <ul class="pricing-table-list">
                    <li>Appreciated!</li>
            

                <li><form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_top">
<input type="hidden" name="cmd" value="_s-xclick">
<input type="hidden" name="hosted_button_id" value="4GG2FN8U7TLDG">
<input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" border="0" name="submit" alt="PayPal - The safer, easier way to pay online!">
<img alt="" border="0" src="https://www.paypalobjects.com/en_US/i/scr/pixel.gif" width="1" height="1">
</form></li></ul>
				
            </div>
        </div>

        <div class="pure-u-2 pure-u-md-1-4">
            <div class="pricing-table pricing-table-biz pricing-table-selected">
                <div class="pricing-table-header">
                    <h2>Buy me a pizza!</h2>

                    <span class="pricing-table-price">
                        $10 <span></span>
                    </span>
                </div>

                <ul class="pricing-table-list">
                    <li>Even nerds have to eat.</li>
          

                <li><form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_top">
<input type="hidden" name="cmd" value="_s-xclick">
<input type="hidden" name="hosted_button_id" value="W7EPFQ3ZCFGDE">
<input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" border="0" name="submit" alt="PayPal - The safer, easier way to pay online!">
<img alt="" border="0" src="https://www.paypalobjects.com/en_US/i/scr/pixel.gif" width="1" height="1">
</form></li></ul>
				
            </div>
        </div>
		
        <div class="pure-u-2 pure-u-md-1-4">
            <div class="pricing-table pricing-table-free">
                <div class="pricing-table-header">
                    <h2>Buy me a steak!</h2>

                    <span class="pricing-table-price">
                        $20 <span></span>
                    </span>
                </div>
				
                <ul class="pricing-table-list">
                    <li>Sometimes, nerds even eat REAL food!</li>
                <li><form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_top">
<input type="hidden" name="cmd" value="_s-xclick">
<input type="hidden" name="hosted_button_id" value="N3MQ2WLDY3AYL">
<input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" border="0" name="submit" alt="PayPal - The safer, easier way to pay online!">
<img alt="" border="0" src="https://www.paypalobjects.com/en_US/i/scr/pixel.gif" width="1" height="1">
</form></li></ul>
				
                

            
			</div>
        </div>
		
		
</div> <!-- end l-content -->

<div class="footer l-box">
    <p>
        Thank you for your support. You can reach me on reddit as <a href="http://reddit.com/u/w0nk0">w0nk0</a> or under Cmdr W0nk0 in-game.
    </p>
</div>




</body>
</html>

"""
from PySide.QtCore import *
from PySide.QtGui import *
import sys
from PySide.QtWebKit import QWebView

class DonateWebView(QWebView):
    def __init__(self,parent=None):
        global html
        super(DonateWebView,self).__init__(parent)
        self.setHtml(html)
        self.setWindowTitle("Thank you for your consideration!")
        self.resize(900,980)


def write_html(filename):
    with open(filename,"wt") as f:
        f.write(html)


if __name__ == "__main__":		

    app = QApplication(sys.argv)
    w = DonateWebView()

    w.show()
    sys.exit(app.exec_())

