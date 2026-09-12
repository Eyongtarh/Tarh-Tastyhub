# Features

Tarh Tastyhub is a complete online food ordering platform designed to support customers and restaurant staff through a role based system.

Key features include:
- User authentication and authorisation
- Category and dish browsing
- Category/dish filtering and sorting
- Featured dishes availability
- Shopping bag and checkout
- Secure Stripe payments
- Order tracking and confirmations
- Promotions and discounts
- Role based staff and admin access control

## Access to pages according to the user role

| Page Name              | Logged out | Customers (Shoppers) | Staff | Admin |
| ----------------------- | ----------- | ---------------------- | ------- | ----- |
| Home                    | Yes         | Yes                     | Yes   | Yes   |
| Login                   | Yes         | Yes                     | Yes   | Yes   |
| Sign Up                 | Yes         | Yes                     | Yes   | Yes   |
| Logout                  | Yes         | Yes                     | Yes   | Yes   |
| Dish Category           | Yes         | Yes                     | Yes   | Yes   |
| Dish Details            | Yes         | Yes                     | Yes   | Yes   |
| All Dishes              | Yes         | Yes                     | Yes   | Yes   |
| Bag                     | No          | Yes                     | Yes   | Yes   |
| Profile                 | No          | Yes                     | Yes   | Yes   |
| Edit profile            | No          | Yes                     | Yes   | Yes   |
| Update profile          | No          | Yes                     | Yes   | Yes   |
| Change password         | No          | Yes                     | Yes   | Yes   |
| Delete account          | No          | Yes                     | Yes   | Yes   |
| Order history           | No          | Yes                     | Yes   | Yes   |
| Order History Details   | No          | Yes                     | Yes   | Yes   |
| Checkout                | No          | Yes                     | Yes   | Yes   |
| Subscribe for Email     | Yes         | Yes                     | Yes   | Yes   |
| Categories              | Yes         | Yes                     | Yes   | Yes   |
| Add category            | No          | No                      | Yes   | Yes   |
| Edit category           | No          | No                      | Yes   | Yes   |
| Delete category         | No          | No                      | Yes   | Yes   |
| Add Dish                | No          | No                      | Yes   | Yes   |
| Edit Dish               | No          | No                      | Yes   | Yes   |
| Delete Dish             | No          | No                      | Yes   | Yes   |
| Contact                 | Yes         | Yes                     | Yes   | Yes   |
| Update order status     | No          | No                      | Yes   | Yes   |
| Cancel Order            | No          | No                      | Yes   | Yes   |
| View Order Details (Admin) | No       | No                      | Yes   | Yes   |
| Print Order Receipt     | No          | No                      | Yes   | Yes   |

## Main Features

Each page has the same header and footer.

### Header

The header contains the navbar and free delivery information.

#### The navbar has three sections

1. Logo section, on the left. It contains the logo "Tarh Tastyhub". If clicked, it redirects you to the home page.

2. The middle section contains links to the Home page, dish category, browse dishes, checkout, and contact.

3. The customer's section, visible to all users, sits on the right alongside the admin dashboard and bag icon:

    - If the user is logged in, the customer's section has the following features:

        + Profile button, which redirects the user to the profile page
        + Logout button, which redirects the user to the home page

    - If the user is logged out, the customer's section has the following features:

        + Login button, which redirects the user to the login page
        + Sign Up button, which redirects the user to the sign up page

    - If the user is logged in as staff, the customer's section additionally has the following feature, visible only to staff:

        + Admin Dashboard button, which redirects staff to the Admin Dashboard page

#### Free Delivery Information

The free delivery discount limit is placed under the navbar and is visible to all.

#### Header images for large screens and mobile devices

The simplistic design of the header is based on the decision to make the web app easy to use for everyone.

*Header above is for large devices with screen sizes greater than 991px*

![Header. Tablets](documentation/features/header_tablets.png)

*Header on devices with a screen width of up to 991px uses a hamburger icon*

![Header. Mobiles](documentation/features/header_mobile.png)

### Footer

![Footer Large devices](documentation/features/footer_page.png)

The footer has the following features:

- Logo name and link to home page.

- Dish category and browse dishes links.

- Contact button, which allows the user to send an email as feedback to the admin.

- Privacy Policy button, which redirects to the privacy policy page.

- Terms and Conditions button, which redirects to the terms and conditions page.

- Social media buttons: Facebook is linked to with a button.

- Subscription to the newsletter via a search bar, handled by Mailchimp.

*Footer is slightly different on mobile devices*

![Footer. Mobile](documentation/features/footer_mobile.png)

### Home page

The home page has three sections, as follows:

- Hero section:

This section has a yellow "Order" button at the centre, which redirects to the dishes page. There is also an eye catching image in the background of the hero section.

![Hero section. Hero Section](documentation/features/home_hero.png)

- Featured Dishes:

This section displays featured dishes in order, so popularity can be a good indicator of which dishes to try first.

![Hero section. Hero Section](documentation/features/home_featured.png)

- Testimonials section:

This section presents testimonials from the store's customers and aims to give visitors an idea of the store's quality.

![Hero section. Hero Section](documentation/features/home_testimonials.png)

*Home page is slightly different on mobile devices*

![Home page. Mobile](documentation/features/home_page_mobile.png)

### Dishes Category page and Browse Dishes page

- The dishes category page displays the category clicked; Browse Dishes displays all the dishes. Both pages share the same layout, showing a search bar and search links for finding dishes. Dishes can be searched by All, category, price, dietary type, or ingredients.

- Below the search bar and search buttons, dishes are displayed in card format. Each card includes the dish image, name, description, size, price, quantity buttons to add to or reduce from the bag, an add to bag button, and a link to view details.

![Dishes Category/Browse Dishes page](documentation/features/category_browse.png)

### Dish Detail page

- This page displays when you click view details on a dish card shown on the Dishes category or Browse Dishes page.

- The view detail page displays the dish image, name, description, size, price, quantity buttons to add to or reduce from the bag, an add to bag button, ingredients, dietary information, and a link to browse dishes.

![View Detail page](documentation/features/view_detail_page.png)

### Checkout

- If logged out, clicking the checkout link redirects you to the sign in or sign up page.

- If logged in, clicking the checkout link redirects you to the checkout page if there are items in the bag. If there are no items in the bag, a message displays saying your bag is empty, and you are redirected to your bag page.

#### Your bag page

##### Logged out

- If logged out, clicking the checkout bag icon redirects you to the sign in or sign up page.

##### Logged in

- If logged in, clicking the navbar checkout button, or the bag icon at the top right corner, redirects you to your bag page.

- When there are no items in the bag, the page displays "Your bag is empty" and a link to browse dishes.

![Your bag is empty page](documentation/features/empty_bag_page.png)

- When there is an item in the bag, your bag page displays a dish card for each item in the bag and a proceed to checkout card.

- The dish card displays the dish image, name, description, size, price, quantity buttons to add to or reduce from the bag, and a link to remove the item from the bag. If there is one item in the bag and the remove link is clicked, the item is removed, the page shows your bag is empty, and a success message for the removed item displays.

- The proceed to checkout card displays an order summary of the subtotal cost, delivery cost, total cost, and a link to proceed to checkout. Clicking the proceed to checkout link redirects you to the checkout page.

![Your bag with dish page](documentation/features/dish_in_bag.png)

#### Checkout page, logged in

- When there is an item in the bag, clicking checkout on the navbar links redirects you to the checkout page. This page displays two cards: your order card and enter your details card.

- Your order card displays the dish or dishes' name(s), portion size(s), quantity, subtotal cost, delivery cost, total cost, and a link to continue shopping.

- Enter your details card displays a form to enter details for card payment. Customers can select delivery or pickup. Pickup displays the pickup time. When the form is correctly filled in, the Pay Now button can be clicked, and payment for the dish or dishes proceeds to the success page.

- When a delivery order is made:

![Delivery Order](documentation/features/delivery_order.png)

- When a pickup order is made:

![Pickup Order](documentation/features/pickup_order.png)

#### Success page, logged in

- The success page displays confirmation of a successful payment from checkout, along with the customer's details, order number, a confirmation email sent message, a link to go to the profile page, the dish or dishes' name(s), portion size(s), quantity, subtotal cost, delivery cost, grand total cost, and a link to continue shopping.

- When a delivery order is successful:

![Delivery Success](documentation/features/delivery_success.png)

- When a pickup order is successful, delivery is always free:

![Pickup Success](documentation/features/pickup_success.png)

#### Email page, logged in

These are emails received at different points during the customer's order:

- When a delivery order is successful:

![Delivery order email](documentation/features/delivery_email.png)

- When a pickup order is successful:

![Pickup order email](documentation/features/pickup_email.png)

- When an order status is updated by an admin, for example, order status updated to ready for pickup:

![Order Status](documentation/features/order_status_ready_pickup.png)

### Feedback page

Clicking the contact link on the navbar redirects you to the feedback page. The page contains two main sections: Contact and Company Information, and the customer feedback form.

![Feedback page](documentation/features/feedback_page.png)

#### Contact and Company Information

This displays business details in three cards, as follows:

- Address: Ekpaw 12, Gothenburg

- Phone: +46 073 344 99 11

- Email: tarhtastyhub@gmail.com

- Opening Hours:
Mon–Fri: 07:00 – 22:00
Sat–Sun: 07:00 – 21:00

#### Customer feedback form

The customer feedback form displays a form and a link to submit feedback. This is possible for both authenticated and anonymous users.

- Authenticated Users

For authenticated users, the username is displayed, and the name and email fields are automatically filled in and hidden. This improves the user experience and reduces input effort. When the subject and message are filled in and submit feedback is clicked, the form submits to the admin and displays a successful submission message.

![Feedback authenticated page](documentation/features/feedback_page1.png)

- Anonymous Users

Anonymous users must manually enter the required information: name, email, subject, and message. Clicking submit feedback then submits the form to the admin and displays a successful submission message.

![Feedback Anonymous page](documentation/features/feedback_page2.png)

### My profile page, logged in

Clicking the user name at the top right corner of the navbar reveals the profile link on large screens; on mobile screens, click the hamburger icon. Clicking Profile redirects you to the profile page, which contains the logged in user's primary data.

- It contains two cards: the default delivery information card and the my orders card.

- The default delivery information card displays primary address information inputs, a link to update information, a link to change password, and a link to delete account.

- The my orders card displays order history, with each order linking to the checkout success page, where the customer can see order details and order status on a progress bar.

- My profile with no order history:

![My profile with no order](documentation/features/my_profile_no_order.png)

- My profile with order history:

![My profile with order](documentation/features/my_profile_with_order.png)

#### Update Profile page, logged in

In the default delivery information card, once the form is filled in and Update Profile is clicked, a message is displayed at the top right corner confirming the profile update was successful.

![Update Profile page](documentation/features/update_profile_page.png)

#### Delete Account page, logged in

In the default delivery information card, at the bottom right, there is a delete account link.

- Clicking the delete account link redirects you to the delete account page, to confirm or cancel account deletion. If Cancel is clicked, you are redirected to the my profile page.

![Delete Account confirmation](documentation/features/confirm_delete_account.png)

##### Delete Account Confirmation page, logged in

- Clicking delete account redirects you to a page to confirm permanent deletion of the account, or cancel. If Cancel is clicked, you are redirected to the my profile page.

![Delete Account permanently](documentation/features/permanent_delete_account.png)

- If Delete Permanently is clicked, you are redirected to the home page, and a message is displayed at the top right corner confirming the account was deleted successfully.

![Delete Account Success](documentation/features/delete_account_success.png)

#### Change password page in my profile, logged in

In the default delivery information card, at the bottom left, there is a change password link.

- Clicking the change password link redirects you to the change password page.

![Password Change](documentation/features/change_password.png)

#### Checkout Success page, logged in

In the my orders card, which displays order history, each order links to the checkout success page, where the customer can see order details and order status on a progress bar.

- Clicking an order number redirects you to the checkout success page. This page displays a status progress bar, the dish or dishes' name(s), portion size(s), quantity, subtotal cost, delivery cost, grand total cost, a link to continue shopping, and a link to track the order.

![Checkout success](documentation/features/checkout_success_page.png)

##### Track order page, logged in

Clicking the track order link on the checkout success page redirects you to the track order page. It displays only the progress bar for the order shown on the checkout success page, along with a link to continue shopping and a link to go to the my profile page.

![Track order](documentation/features/track_order_page.png)

### Admin Dashboard page, logged in

- Clicking the user name at the top right corner of the navbar reveals the admin dashboard link, visible only to staff, on large screens; on mobile screens, click the hamburger icon. Clicking Admin Dashboard redirects you to the admin dashboard page.

- The admin dashboard is a secure, role based management interface for Tarh Tastyhub, allowing staff to efficiently manage orders, dishes, categories, and customer feedback from a single, responsive dashboard.

- This dashboard is built with a strong focus on usability, accessibility, and order management.

![Admin Dashboard page](documentation/features/admin_page.png)
![Admin Dashboard page](documentation/features/admin_page2.png)
![Admin Dashboard page](documentation/features/admin_page3.png)
![Admin Dashboard page](documentation/features/admin_page4.png)
![Admin Dashboard page](documentation/features/admin_page5.png)

#### Order Management

##### View full order details

View full order details in a modal (customer info, delivery, line items, totals) when View Details is clicked.

![Admin Dashboard page view details](documentation/features/admin_view_details.png)
![Admin Dashboard page view details](documentation/features/admin_view_details2.png)

##### Update order status

Update order status (Pending, Preparing, Out for Delivery / Ready for Pickup, Completed). When the appropriate status is selected and Update is clicked, the customer is notified by email of the order's current status, worded according to whether the order is marked for pickup or delivery.

- Updating a delivery order from pending to preparing:

![Admin Dashboard page delivery update](documentation/features/delivery_update.png)
![Admin Dashboard page delivery update](documentation/features/delivery_update2.png)
![Admin Dashboard page delivery update](documentation/features/delivery_update3.png)

- Updating a pickup order from pending to ready for pickup:

![Admin Dashboard page pickup update](documentation/features/pickup_update.png)
![Admin Dashboard page pickup update](documentation/features/pickup_update2.png)
![Admin Dashboard page pickup update](documentation/features/pickup_update3.png)

##### Cancel active orders

When Cancel is clicked, the order is cancelled if its status is not yet Completed. If the order status is already Completed, it cannot be cancelled here.

- If the order status is not Completed, clicking Cancel redirects you to the order cancel page to confirm cancellation or go back to the dashboard. If Confirm Cancellation is clicked, the order is cancelled and a confirmation message displays at the top right corner.

![Admin Dashboard page cancel order](documentation/features/cancel_order.png)
![Admin Dashboard page cancel order](documentation/features/cancel_order2.png)

If the order status is Completed, the cancel option is not available:

![Admin Dashboard page order status: completed](documentation/features/no_cancel_order.png)

##### Print individual orders

When the print button is clicked, it redirects you to a print page. It displays a print button and a button to go back to the dashboard. Clicking print opens the browser's print dialogue, where you can print, save as a PDF, or cancel.

![Admin Dashboard page print](documentation/features/print_order.png)
![Admin Dashboard page print](documentation/features/print_order1.png)

#### Dish Management pages

In the admin dashboard, staff can view all available dishes, along with their category and base price. Staff can also add, edit, and delete dishes directly from the admin dashboard.

##### Add dishes

The first button at the top left of the admin dashboard is the Add Dish link. Clicking it redirects you to the add dish page, with a form to fill in; click Add Dish at the bottom to save it, or Cancel to return to the admin dashboard.

![Admin Dashboard add dish page](documentation/features/add_dish.png)

##### Edit dishes

The dishes card section of the admin dashboard lists all dishes, with Edit and Delete side by side for each one. Clicking Edit redirects you to the edit dish page, with a form to fill in; click Edit Dish at the bottom to save changes, or Cancel to return to the admin dashboard.

![Admin Dashboard edit dish page](documentation/features/edit_dish.png)

##### Delete existing dishes

The dishes card section of the admin dashboard lists all dishes, with Edit and Delete side by side for each one. Clicking Delete redirects you to the delete dish page, to confirm deletion or cancel. If Confirm Delete is clicked, the dish is deleted, a message confirms it was deleted successfully, and you are redirected to the admin dashboard. Clicking Cancel also redirects you to the admin dashboard.

![Admin Dashboard delete dish page](documentation/features/delete_dish.png)

#### Category Management pages

In the admin dashboard, staff can view all available categories, and can also add, edit, and delete categories directly from the admin dashboard.

##### Add category

The second button at the top right of the admin dashboard is the Add Category link. Clicking it redirects you to the add category page, with a form to fill in; click Add Category at the bottom to save it, or Cancel to return to the admin dashboard.

![Admin Dashboard add category page](documentation/features/add_category.png)

##### Edit category

The categories card section of the admin dashboard lists all categories, with Edit and Delete side by side for each one. Clicking Edit redirects you to the edit category page, with a form to fill in; click Edit Category at the bottom to save changes, or Cancel to return to the admin dashboard.

![Admin Dashboard edit category page](documentation/features/edit_category.png)

##### Delete category

The categories card section of the admin dashboard lists all categories, with Edit and Delete side by side for each one. Clicking Delete redirects you to the delete category page, to confirm deletion or cancel. If Confirm Delete is clicked, the category is deleted, a message confirms it was deleted successfully, and you are redirected to the admin dashboard. Clicking Cancel also redirects you to the admin dashboard.

![Admin Dashboard delete category page](documentation/features/delete_category.png)

#### Customer Feedback section in admin dashboard

View customer feedback submissions, filtered by All, Unread, or Handled. Feedback can be marked as handled or unhandled, and the list is paginated for improved performance.

![Admin Dashboard feedback section](documentation/features/feedback_section.png)

## Allauth and Access pages

### 403, 404, and 500 pages

It handles three types of errors:

- 403 error
- 404 error
- 500 error

Example of an error page:

![404 error](documentation/features/allauth_access_404.png)

### Logout Page

![Logout Page](documentation/features/allauth_access_logout.png)

### Sign Up Page

![Sign Up Page](documentation/features/allauth_access_sign_up.png)

### Login Page

![Login Page](documentation/features/allauth_access_login.png)

### Forgot Password Page

![Forgot Password Page](documentation/features/allauth_access_reset_password_request.png)
