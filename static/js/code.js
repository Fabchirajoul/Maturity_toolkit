document.addEventListener("alpine:init", () => {
  Alpine.data("AutomatedDigitalMaturity", () => {
    return {
      Admin_Home_Page: false,

      // Creating the sections
      Create_Business_Sector: true,
      Create_Measuring_Element: false,
      Create_Rating: false,
      Create_Sub_Category: false,
      Create_Questions: false,
      admininstrator_user_creating: false,

      // Updating the sections
      Update_Business_Sector: false,
      Update_Measuring_Element: false,
      Update_Rating: false,
      Update_Sub_Category: false,
      Update_Questions: false,
      choose_a_question_to_answer: false,

      // userAccount logics
      select_your_business_sector: true,
      displayed_tiers_per_business_sector: false,
      // choose_sub_category: false,

      // toolkit computation
      // Maturity_toolkit_feedback: false,

      openUserAccount(UserSection) {
        this.select_your_business_sector = true;
        this.displayed_tiers_per_business_sector = false;
        // this.choose_sub_category = false;
        // this.Maturity_toolkit_feedback = false;
        

        if (UserSection === "displayed_tiers_per_business_sector") {
          this.select_your_business_sector = false;
          this.displayed_tiers_per_business_sector = true;
          
 
          
        } else if (UserSection === "choose_sub_category") {
  
          
        } else if (UserSection === "Maturity_toolkit_feedback") {
          // this.select_your_business_sector = false;
          // this.choose_measuring_element = false;
          // this.choose_sub_category = false;
          // this.Maturity_toolkit_feedback = true;
          // this.admininstrator_user_creating = false;
        }
      },

      openHome(currentSection) {
        this.Admin_Home_Page = false;
        this.Create_Business_Sector = true;
        this.Create_Measuring_Element = false;
        this.Create_Rating = false;
        this.Create_Sub_Category = false;
        this.Create_Questions = false;
        this.Update_Business_Sector = false;
        this.Update_Measuring_Element = false;
        this.Update_Rating = false;
        this.Update_Sub_Category = false;
        this.Update_Questions = false;
        this.admininstrator_user_creating = false;

        if (currentSection == "Update_Questions") {
          this.Admin_Home_Page = false;
          this.Create_Business_Sector = false;
          this.Create_Measuring_Element = false;
          this.Create_Rating = false;
          this.Create_Sub_Category = false;
          this.Create_Questions = false;
          this.Update_Business_Sector = false;
          this.Update_Measuring_Element = false;
          this.Update_Rating = false;
          this.Update_Sub_Category = false;
          this.Update_Questions = true;
          this.admininstrator_user_creating = false;
        } else if (currentSection == "Create_Measuring_Element") {
          this.Admin_Home_Page = false;
          this.Create_Business_Sector = false;
          this.Create_Measuring_Element = true;
          this.Create_Rating = false;
          this.Create_Sub_Category = false;
          this.Create_Questions = false;
          this.Update_Business_Sector = false;
          this.Update_Measuring_Element = false;
          this.Update_Rating = false;
          this.Update_Sub_Category = false;
          this.Update_Questions = false;
          this.admininstrator_user_creating = false;
        } else if (currentSection == "Create_Rating") {
          this.Admin_Home_Page = false;
          this.Create_Business_Sector = false;
          this.Create_Measuring_Element = false;
          this.Create_Rating = true;
          this.Create_Sub_Category = false;
          this.Create_Questions = false;
          this.Update_Business_Sector = false;
          this.Update_Measuring_Element = false;
          this.Update_Rating = false;
          this.Update_Sub_Category = false;
          this.Update_Questions = false;
          this.admininstrator_user_creating = false;
        } else if (currentSection == "Create_Sub_Category") {
          this.Admin_Home_Page = false;
          this.Create_Business_Sector = false;
          this.Create_Measuring_Element = false;
          this.Create_Rating = false;
          this.Create_Sub_Category = true;
          this.Create_Questions = false;
          this.Update_Business_Sector = false;
          this.Update_Measuring_Element = false;
          this.Update_Rating = false;
          this.Update_Sub_Category = false;
          this.Update_Questions = false;
          this.admininstrator_user_creating = false;
        } else if (currentSection == "Create_Questions") {
          this.Admin_Home_Page = false;
          this.Create_Business_Sector = false;
          this.Create_Measuring_Element = false;
          this.Create_Rating = false;
          this.Create_Sub_Category = false;
          this.Create_Questions = true;
          this.Update_Business_Sector = false;
          this.Update_Measuring_Element = false;
          this.Update_Rating = false;
          this.Update_Sub_Category = false;
          this.Update_Questions = false;
          this.admininstrator_user_creating = false;
        } else if (currentSection == "Update_Business_Sector") {
          this.Admin_Home_Page = false;
          this.Create_Business_Sector = false;
          this.Create_Measuring_Element = false;
          this.Create_Rating = false;
          this.Create_Sub_Category = false;
          this.Create_Questions = false;
          this.Update_Business_Sector = true;
          this.Update_Measuring_Element = false;
          this.Update_Rating = false;
          this.Update_Sub_Category = false;
          this.Update_Questions = false;
          this.admininstrator_user_creating = false;
        } else if (currentSection == "Update_Measuring_Element") {
          this.Admin_Home_Page = false;
          this.Create_Business_Sector = false;
          this.Create_Measuring_Element = false;
          this.Create_Rating = false;
          this.Create_Sub_Category = false;
          this.Create_Questions = false;
          this.Update_Business_Sector = false;
          this.Update_Measuring_Element = true;
          this.Update_Rating = false;
          this.Update_Sub_Category = false;
          this.Update_Questions = false;
          this.admininstrator_user_creating = false;
        } else if (currentSection == "Update_Rating") {
          this.Admin_Home_Page = false;
          this.Create_Business_Sector = false;
          this.Create_Measuring_Element = false;
          this.Create_Rating = false;
          this.Create_Sub_Category = false;
          this.Create_Questions = false;
          this.Update_Business_Sector = false;
          this.Update_Measuring_Element = false;
          this.Update_Rating = true;
          this.Update_Sub_Category = false;
          this.Update_Questions = false;
          this.admininstrator_user_creating = false;
        } else if (currentSection == "Update_Sub_Category") {
          this.Admin_Home_Page = false;
          this.Create_Business_Sector = false;
          this.Create_Measuring_Element = false;
          this.Create_Rating = false;
          this.Create_Sub_Category = false;
          this.Create_Questions = false;
          this.Update_Business_Sector = false;
          this.Update_Measuring_Element = false;
          this.Update_Rating = false;
          this.Update_Sub_Category = true;
          this.Update_Questions = false;
          this.admininstrator_user_creating = false;
        }else if (currentSection == "Admin_Home_Page") {
          this.Admin_Home_Page = true;
          this.Create_Business_Sector = false;
          this.Create_Measuring_Element = false;
          this.Create_Rating = false;
          this.Create_Sub_Category = false;
          this.Create_Questions = false;
          this.Update_Business_Sector = false;
          this.Update_Measuring_Element = false;
          this.Update_Rating = false;
          this.Update_Sub_Category = false;
          this.Update_Questions = false;
          // this.admininstrator_user_creating = true;
        }
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
