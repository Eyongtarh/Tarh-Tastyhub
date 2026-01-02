# Features

Tarh TastyHub is a full-stack online food ordering platform designed to support customers, restaurant, and delivery personnel through a role-based system.

Key features include:
- User authentication and authorization
- Category and dish browsing
- Category/dish filtering and sorting
- Dish availability tracking and notifications
- Shopping bag and checkout
- Secure Stripe payments
- Order tracking and confirmations
- Promotions and discounts
- Multi-role personnel management (Admin, Manager, Kitchen, Delivery)

## Access to pages according to the user role:

| Page Name | Logged out  | Customers  | Manager | Admin |
| --------- | ----------- | ---------- | ------- | ----- |
| Home       | Yes         | Yes        | Yes     | Yes   |
| Login      | Yes         | Yes        | Yes     | Yes   |
| Register   | Yes         | Yes        | Yes     | Yes   |
| Logout     | Yes         | Yes        | Yes     | Yes   |
| Dish Category   | Yes         | Yes        | Yes     | Yes   |
| Dish Details | Yes         | Yes        | Yes     | Yes   |
| All Dishes   | Yes         | Yes        | Yes     | Yes   |
| Bag       | No         | Yes        | Yes     | Yes   |
| Profile   | No         | Yes        | Yes     | Yes   |
| Edit profile   | No         | Yes        | Yes     | Yes   |
| Add address   | No         | Yes        | Yes     | Yes   |
| All addresses   | No         | Yes        | Yes     | Yes   |
| Edit address   | No         | Yes        | Yes     | Yes   |
| My Orders   | No         | Yes        | Yes     | Yes   |
| My Order's Details   | No         | Yes        | Yes     | Yes   |
| Checkout   | No         | Yes        | Yes     | Yes   |
| Create newsletter-promo Email | No         | No         | Yes     | Yes   |
| Categories | No         | Yes         | Yes     | Yes   |
| Add category | No         | No         | Yes     | Yes   |
| Edit category | No         | No         | Yes     | Yes   |
| Delete category | No         | No         | No     | Yes   |
| Add Dish | No         | No         | Yes     | Yes   |
| Edit Dish | No         | No         | Yes     | Yes   |
| Delete Dish | No         | No         | No     | Yes   |

| Update order status | No         | No         | No     | Yes + Staff  |
| Cnecel Order | No         | No         | No     | Yes   |
| View order Detail| No         | No         | No     | Yes   |
| Print order's Receipt | No         | No         | No     | Yes   |


## Main Features:

Each page has same header and footer.

### Header:

The header contains the navbar and free delivery information.

#### The Navbar has five subsections:

1. Logo section, which is the first by the left. I contains the logo if Tarh Tarstyhub.

2. The second section contains links to Home page, dish category, browse dishes, checkout, and contact. This section is at the middle.

3. Customer's section, which is visible for all users is by the right with admin dashboard and bag icon/count :

    - if the user is logged in, the Navbar has the following features:
      
        - logo, which redirects to the home page

        - Profile button, which redirects the user to the profile page

        - Logout button, which redirects the user to the login page


    - if the user is logged out, the Navbar has the following features:
    
        - logo, which redirects to the home page

        - Login button, which redirects the user to the login page

        - SignUp button, which redirects the user to the signup page

4. Admin Dashboard section, which is visible only for Staff:

    It has Admin Dashboard button, which is visible only for staff. When this button is clicked, it redirects the staff to thee Adnin Dashboard page .

#### Fee Delivery Information

   Free delivery discount limit is placed under the navbar which is visible to all.

The simplistic design of the header is based on the decision to make the use of the web app easy for all users.

*Header above is for large devices with screen sized greater than 991px*

![Header. Tablets](documentation/features/header_tablets.png)

*Header on devices with screen sizes with max-width of 991px uses a hamburger icon*

![Header. Mobiles](documentation/features/header_mobile.png)

### Footer:

![Footer Large devices](documentation/features/footer_page.png)

Footer has the following features:

- logo name and link to home page

- Dishe category and browse dishes links.

- Contact button, which allows the user to send an email as feedback to admin;

- Privacy Policy button, which redirects the privacy policy page;

- Terms and Conditions button, which redirects the terms and conditions page;

- Social media buttons: Facebook is linked to with a button;

- Subscription to mailchimp.com search bar.

*Footer is slightly different on the mobile devices*

![Footer. Mobile](documentation/features/footer_mobile.png)

### Home page:

The home page has three sections as follows:

- Hero section:

This section has an order yellow at the center which redirects to dishes page. There is also an eye-catching image at the background of the hero section.

![Hero section. Hero Section](documentation/features/home_hero.png)

- Featured Dishes:

This section displays featured dishes in the order line, so popular dishes order can be a good indicator if neccessary.

![Hero section. Hero Section](documentation/features/home_featured.png)

- Testimonials section:

This section presents the testimonials of the store customers and aims to give the user an idea of the store's quality.

![Hero section. Hero Section](documentation/features/home_testimonials.png)

*Home page is slightly different on the mobile devices*

![Home page. Mobile](documentation/features/home_page_mobile.png)

###  Dishes Category page and Browse Dishes page:

- These pages display on one page showing search bar and search links to search dishes.Dishes can be search by category, price,dietary type or ingredients.

- Below the search bar and search buttons, dishes are displayed in card format. Each card includes dish image, name, description, size ,price, quantity buttons to add to or reduce from bag, add to bag button, and a link to view details.


![Dishes Categor/Browse Dishes page](documentation/features/category_browse.png)

###  Dish Detail page:

- This page displays when you click view details on a dish card displayed in a Dishes category or browse dishes page.

- View detail displays, dish image, name, description, size ,price, quantity buttons to add to or reduce from bag, add to bag button, ingredients, dietary information and a link to browse dishes.

![View Detail page](documentation/features/view_detail_page.png)

### Checkout:
A click on link checkout or bag icon at the top right corner on the navbar redirects you to your bag page, there after to the checkout page.

#### Your bag page

- When clicked on navbar checkout button or bag icon at the top right corner, it redirects you to your bag page.
- When there are no items in the bag, the page displays "your bag is empty" and a link to browse dishes"

![Your bag is empty page](documentation/features/empty_bag_page.png)

- When there is an item in the bag, your bag page displays a dish card of each item in bag and a proceed to checkout card. 

- The dish card displays dish image, name, description, size ,price, quantity buttons to add to or reduce from bag, linke to remove item from bag. If one item in bag and linke to remove item from bag is clicked, item is removed and page shows your bag is empty.

- The proceed to checkout card displays order summary of: subtotal cost, delivery cost, total cost, and a link to proceed to checkout. If, proceed to checkout link is clicked, it redirects you to checkout page.

![Your bag with dish page](documentation/features/dish_in_bag.png)

#### Checkout page:

- This page displays two cards, your order card and enter your details card.

- Your order card displays, dish or dishes name(s), portion size(s), quantity, subtotal cost, delivery cost, total cost, and a link to contintinue shopping.

- Enter your details card displays form to enter details for card payment. Customer can select deivery or pick up. Pickup displays pickup time. When form is fully filed, the pay now link can be clicked, and payment for dish/dishes will proceed to success page.

- When a delivery order is made:

![Delivery Order](documentation/features/delivery_order.png)

- When a delivery order is made:

![Pickup Order](documentation/features/pickup_order.png)

#### Success page:

- The success page displays successfull payment from checkout, displays customer's details, delivery order number, confirmation email sent message, a link to go to profile page, dish or dishes name(s), portion size(s), quantity, subtotal cost, delivery cost, grand total cost, and a link to contintinue shopping.

- When a delivery order is succesfull:

![Delivery Success](documentation/features/delivery_success.png)

- When a pickup order is succesfull, delivery is always free:

![Pickup Success](documentation/features/pickup_success.png)

#### Email page:

These are emails received at different point in the customers proceedings:

- When a delivery order is succesfull:
![Delivery order email](documentation/features/delivery_email.png)

- When a pickup order is succesfull:

![Pickup order email](documentation/features/pickup_email.png)

### Feedback page
A click on link contact on the navbar redirects you to feedback page. The page contains two main sections: Contact and company information, and customer feedback form.

![Feedback page](documentation/features/feedback_page.png)

#### Contact & Company Information

This displays business details in three cards as follows:

- Address: Ekpaw 12 ,othenburg

-  Phone +46 073 344 99 11 Email , tarhtastyhuh@gmail.com

- Opening Hours
Mon–Fri: 07:00 – 22:00
Sat–Sun: 07:00 – 21:00

#### Customer feedback form

Customer feedback form displays a form and a link to submit feedback. This is possible for both authenticated and anonymous users.

- Authenticated Users

For authenticated users, username is displayed, name and email fields are automatically filled and hidden. This improves user experience and reduced input effort.When subject and message is fill and a click on submit feedback, the form submits to admin and displays a successful submission message.

![Feedback authenticated page](documentation/features/feedback_page1.png)

- Anonymous Users

Anonymous users must manually enter required information; name, email, subject and message then a click on submit feedback, the form submits to admin and displays a successful submission message.

![Feedback Anonymous page](documentation/features/feedback_page2.png)

### My profile page:

A click at the top right corner on the navbar on user name reveals the profile link on large screen, on mobile screens, click hamburger icon. Click profiles and it redirects you to profiles page containing primary data on the customer for the logged-in user.

- It contains two cards; default delivery information card and my order card. 

- Default delivery information card displays primary address information inputs , a link  to update information, a link to change password, and a link to delete account.

- My order card displays information on order history and each order is a link to checkout success page where customer can see order details and order status on a progress bar.

- My profile with no order history:

![My profile with no order](documentation/features/my_profile_no_order.png)

- My profile with no order history:

![My profile with order](documentation/features/my_profile_with_order.png)

#### Update Profile page: 

In the default delivery information card, form is filled and update profile link is cliked, a message is displaced at the top right corner confirming profile update was successful.

![Update Profile page](documentation/features/update_profile_page.png)

#### Delete Account page:

In the default delivery information card, at the bottom, right, you have delete account link.
- If delete account link is cliked, it redirects you to delete account page , to firm or cancel profile deletion. I cancelled is click, it redirects you to my profile page.

![Delete Account confirmation](documentation/features/confirm_delete_account.png)

##### Delete Account Confirmation page:
- If delete account is clicked, it redirects you to confirm permanent deletion of account page or cancel. If cancel if clicked, it redirects you to my profile page.

![Delete Account permanently](documentation/features/permanent_delete_account.png)

- If delete permanently is clicked, it redirects you to home page, a message is displaced at the top right corner confirming account was deleted successfully.

![Delete Account Success](documentation/features/delete_account_success.png)

#### Change password page in my profile:

In the default delivery information card, at the bottom, left, you have change password link.
- If change password link is cliked, it redirects you to change password page to change password.

![Password Change](documentation/features/change_password.png)

#### Checkout Success page:
In the my order card, which displays information on order history and each order is a link to checkout success page where customer can see order details and order status on a progress bar.

- A click on an order number redirects you to checkout success page. This page displays a status progress bar , dish or dishes name(s), portion size(s), quantity, subtotal cost, delivery cost, grand total cost, a link to contintinue shopping and a link to only track order.

![Checkout success](documentation/features/checkout_success_page.png)

- Checkout success progress bar update

##### Track order page:

A click on the link track order in checkout success page redirects you to track order page. It displays only the progress bar of the order(s) in checkout success page. It also includes a link to contintinue shopping and a link go to my profile page.

![Track order](documentation/features/track_order_page.png)

### Admin Dashboard page:

- A click at the top right corner on the navbar on user name reveals the admin dashboard only for staff and on large screens, on mobile screens, click hamburger icon. Click admin dashboard and it redirects you to admin dashboard page.

- The admin dashboard is a secure, role-based management interface for Tarh Tastyhub, allowing staff to efficiently manage orders, dishes, categories, and customer feedback from a single, responsive dashboard.

- This dashboard is built with a strong focus on usability, accessibility, and order management.

![Admin Dashboard page](documentation/features/admin_page.png)
![Admin Dashboard page](documentation/features/admin_page2.png)
![Admin Dashboard page](documentation/features/admin_page3.png)
![Admin Dashboard page](documentation/features/admin_page4.png)
![Admin Dashboard page](documentation/features/admin_page5.png)

#### Order Management

##### View full order details

View full order details in a modal (customer info, delivery, line items, totals) when view details is clickes.

 ![Admin Dashboard page view details](documentation/features/admin_view_details.png)
 ![Admin Dashboard page view details](documentation/features/admin_view_details2.png)

##### Update order status 

Update order status (Pending, Preparing, Out for Delivery / Ready for Pickup, Completed)
When the appropriate status is selected, and update button clicked, it update the customer by sending an email with the current status of order depending if the order is marked for pickup or delivery.

- Updating a delivery order pending to preparing

![Admin Dashboard page delivery update](documentation/features/delivery_update.png)
![Admin Dashboard page delivery update](documentation/features/delivery_update2.png)
![Admin Dashboard page delivery update](documentation/features/delivery_update3.png)

- Updating a pickup order pending to ready for pickup

![Admin Dashboard page pickup update](documentation/features/pickup_update.png)
![Admin Dashboard page pickup update](documentation/features/pickup_update2.png)
![Admin Dashboard page pickup update](documentation/features/pickup_update3.png)

##### Cancel active orders
When the cancel button is clicked, the order is cancel if order status is not completed. But completed order staus is completed, it can not be cancelled here.

- If order status is not completed, a click on cancel redirects you to order cancel page to confirm cancellation or go back to dashboard. If confirm cancellation button is clicked, order is cancelled and confirmation messgae displays at the top right corner.

![Admin Dashboard page cancel order](documentation/features/cancel_order.png)
![Admin Dashboard page cancel order](documentation/features/cancel_order2.png)

If oder status is completed, cancel option is not available.

![Admin Dashboard page order status: completed](documentation/features/no_cancel_order.png)

##### Print individual orders

When the print button is clicked, it redirects you to a print page. It displays a print button and button to lead back to dashboard. If print button is clicked, it redirects to print system, save to print out or cancell.

![Admin Dashboard page print](documentation/features/print_order.png)
![Admin Dashboard page print](documentation/features/print_order1.png)

#### Dish Management pages

In the admindashboard staff can view all available dishes, display dish category and base price. Staff can also add, edit, and delete dishes directly from the admin dashboard.

##### Add dishes
The first button at the top left of the admin dashboard is add dish link. If clicked, it redirects you to the add dish page with a form to fill and add dish through a click at the bottom, add dish, or click cancel to redirect you to the admin dashboard.
![Admin Dashboard add dish page](documentation/features/add_dish.png)

##### Edit dishes
The second card section of the admin dashboard accomodates dishes. Edit and delete are side by side for each dish. If edit is clicked, it redirects you to the edit dish page with a form to fill and edit through a click at the bottom, edit dish, or click cancel to redirect you to the admin dashboard.

![Admin Dashboard edit dish page ](documentation/features/edit_dish.png)

##### Delete existing dishes

The second card section of the admin dashboard accomodates dishes. Edit and delete are side by side for each dish. If delete is clicked, it redirects you to the delete dish page with a form to confirm delete or cancel. If confirm delete is clicked, it deletes the dish , message displayed as dish successfully deleted and redirects you to admin dashboard. If clicked on cancel, it  redirects you to the admin dashboard.

![Admin Dashboard delete dish page](documentation/features/delete_dish.png)


#### Category Management pages
In the admin dashboard staff can view all available categories, and can also add, edit, and delete categories directly from the admin dashboard.

##### Add category
The second button at the top right of the admin dashboard is add category link. If clicked, it redirects you to the add category page with a form to fill and add category through a click at the bottom, add category, or click cancel to redirect you to the admin dashboard.

![Admin Dashboard add category page](documentation/features/add_category.png)


##### Edit category

The third card section of the admin dashboard accomodates ctegories. Edit and delete are side by side for each category. If edit is clicked, it redirects you to the edit category page with a form to fill and edit through a click at the bottom, edit category, or click cancel to redirect you to the admin dashboard.

![Admin Dashboard edit category page ](documentation/features/edit_category.png)

##### Delete category

The third card section of the admin dashboard accomodates categories. Edit and delete are side by side for each category. If delete is clicked, it redirects you to the delete category page to confirm delete or cancel. If confirm delete is clicked, it deletes the category, message displayed as category successfully deleted and redirects you to admin dashboard. If clicked on cancel, it  redirects you to the admin dashboard.

![Admin Dashboard delete category page](documentation/features/delete_category.png)

#### Customer Feedback section in admin dashboard

View customer feedback submissions, filters feedback by: All , Unread, Handled: Mark feedback as handled or unhandled, paginated feedback list for improved performance.

![Admin Dashboard feedback section](documentation/features/feedback_section.png)


## Allauth and Access pages:

### 403, 404, and 500 pages:

It handles two types of errors:

- 403 error;
- 404 error;
- 500 error;

Example of error:

![404 error](documentation/features/allauth_access_404.png)

### Logout Page:

![Logout Page](documentation/features/allauth_access_logout.png)

### Signup Page:

![Signup Page](documentation/features/allauth_access_sign_up.png)

### Login Page:

![Login Page](documentation/features/allauth_access_login.png)

### Forgot Password Page:

![Forgot Password Page](documentation/features/allauth_access_reset_password_request.png)

