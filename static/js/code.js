document.addEventListener("alpine:init", () => {
  Alpine.data("AutomatedDigitalMaturity", () => {
      return {
          Admin_Home_Page: true,
          manage_business_sector: false,
          manage_user_account: false,
          manage_csv_file_upload: false,
          activate_deactivate_user: false,
          computational_interface_new_business_sector: false,
          computational_interface_update_business_sector: false,
          assign_answer_rating_for_business_functions: false,
          select_business_sector: true,
          select_business_function: false,
          add_new_answer_rating:false,
          update_old_answer_rating:false,

          openHomeBusinessAnalysts(BusinessAnalysts) {
              this.select_business_sector = true;
              this.select_business_function = false;

              if (BusinessAnalysts == "select_business_function") {
                  this.select_business_sector = false;
                  this.select_business_function = true;
              }
          },

          openHome(currentSection) {
              this.Admin_Home_Page = true;
              this.manage_business_sector = false;
              this.manage_user_account = false;
              this.manage_csv_file_upload = false;
              this.activate_deactivate_user = false;
              this.computational_interface_new_business_sector = false;
              this.computational_interface_update_business_sector = false;
              this.assign_answer_rating_for_business_functions = false;
              this.add_new_answer_rating=false;
              this.update_old_answer_rating=false;

              if (currentSection == "manage_business_sector") {
                  this.Admin_Home_Page = false;
                  this.manage_business_sector = true;
              } else if (currentSection == "manage_user_account") {
                  this.Admin_Home_Page = false;
                  this.manage_user_account = true;
              } else if (currentSection == "add_new_answer_rating") {
                this.Admin_Home_Page = false;
                this.add_new_answer_rating = true;
            } else if (currentSection == "update_old_answer_rating") {
                this.Admin_Home_Page = false;
                this.update_old_answer_rating = true;
            } else if (currentSection == "manage_csv_file_upload") {
                  this.Admin_Home_Page = false;
                  this.manage_csv_file_upload = true;
              } else if (currentSection == "activate_deactivate_user") {
                  this.Admin_Home_Page = false;
                  this.activate_deactivate_user = true;
              } else if (currentSection == "computational_interface_new_business_sector") {
                  this.Admin_Home_Page = false;
                  this.computational_interface_new_business_sector = true;
              } else if (currentSection == "computational_interface_update_business_sector") {
                  this.Admin_Home_Page = false;
                  this.computational_interface_update_business_sector = true;
              } else if (currentSection == "assign_answer_rating_for_business_functions") {
                  this.Admin_Home_Page = false;
                  this.assign_answer_rating_for_business_functions = true;
              }
          },

          submitBusinessSector() {
              // Submit the form programmatically
              document.getElementById('business-sector-form').submit();

              // Change the state to show the business function section
              this.$nextTick(() => {
                  this.select_business_sector = false;
                  this.select_business_function = true;
              });
          },

          init() {
              this.startTimerWhyUs();
              this.activeImage = this.images.length > 0 ? this.images[0] : null;
          },

          images: [
              "/static/images/Looping/1.png",
              "/static/images/Looping/2.png",
              "/static/images/Looping/3.jpg",
              "/static/images/Looping/4.png",
          ],
          activeImage: null,

          prev() {
              let index = this.images.indexOf(this.activeImage);
              if (index === 0) index = this.images.length;
              this.activeImage = this.images[index - 1];
          },

          next() {
              let index = this.images.indexOf(this.activeImage);
              if (index === this.images.length - 1) index = -1;
              this.activeImage = this.images[index + 1];
          },

          imageWhyUs: [
              {
                  image: "/static/images/Looping/1.png",
                  text1: "1",
                  text2: "Some few text description will come here. Image will equally be changed for 1 ",
              },
              {
                  image: "/static/images/Looping/2.png",
                  text1: "2",
                  text2: "Some few text description will come here. Image will equally be changed for 2",
              },
              {
                  image: "/static/images/Looping/3.jpg",
                  text1: "3",
                  text2: "Some few text description will come here. Image will equally be changed for 3",
              },
              {
                  image: "/static/images/Looping/4.png",
                  text1: "4",
                  text2: "Some few text description will come here. Image will equally be changed for 4",
              },
              {
                  image: "/static/images/Looping/5.jpg",
                  text1: "5",
                  text2: "Some few text description will come here. Image will equally be changed 5",
              },
              {
                  image: "/static/images/Looping/6.jpg",
                  text1: "6",
                  text2: "Some few text description will come here for. Image will equally be changed 6",
              },
          ],
          currentIndex: 0,

          startTimerWhyUs() {
              setInterval(() => {
                  this.currentIndex = (this.currentIndex + 1) % this.imageWhyUs.length;
                  this.text1 = "";
              }, 5000);
          },
      };
  });
});