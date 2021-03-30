<template>
  <v-app id="inspire">
    <v-navigation-drawer v-model="drawer" app>
      <!--  -->
    </v-navigation-drawer>

    <v-app-bar app>
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>

      <v-toolbar-title>AutoML Vision Demo</v-toolbar-title>
    </v-app-bar>

    <v-main class="grey lighten-3">
      <v-container>
        <v-row>
          <v-col cols="12" sm="8">
            <v-sheet min-height="50vh" rounded="lg">
              <v-stepper v-model="e1">
                <v-stepper-header>
                  <v-stepper-step :complete="e1 > 1" step="1">
                    Upload file
                  </v-stepper-step>

                  <v-divider></v-divider>

                  <v-stepper-step :complete="e1 > 2" step="2">
                    Choose Prediction Type
                  </v-stepper-step>

                  <v-divider></v-divider>

                  <v-stepper-step step="3">
                    Submit
                  </v-stepper-step>
                </v-stepper-header>

                <v-stepper-items>
                  <v-stepper-content step="1">
                    <v-card class="mb-12" color="lighten-1" height="350px">
                      <v-row
                        class="d-flex flex-column justify-center align-center"
                      >
                        <v-col cols="4">
                          <v-file-input
                            accept="image/*"
                            label="File input"
                            v-model="file_url"
                            @change="parse_image"
                          ></v-file-input>
                        </v-col>
                        <v-col cols="4"><p>Or</p></v-col>
                        <v-col cols="4">
                          <v-dialog
                            v-model="dialog"
                            scrollable
                            max-width="800px"
                          >
                            <template v-slot:activator="{ on, attrs }">
                              <v-btn
                                color="info"
                                dark
                                v-bind="attrs"
                                v-on="on"
                                text
                              >
                                Select from Examples
                              </v-btn>
                            </template>
                            <v-card>
                              <v-card-title>Select Image</v-card-title>
                              <v-divider></v-divider>
                              <v-card-text style="height: 350px;">
                                <v-radio-group v-model="image_select" row>
                                  <v-col
                                    cols="3"
                                    v-for="(item, i) in available_files"
                                    :key="i"
                                  >
                                    <v-radio
                                      :label="item.blob_name"
                                      :value="item"
                                    ></v-radio>
                                    <v-img
                                      lazy-src="https://picsum.photos/id/11/10/6"
                                      max-height="150"
                                      max-width="250"
                                      :src="item.url"
                                    ></v-img>
                                  </v-col>
                                </v-radio-group>
                              </v-card-text>
                              <v-divider></v-divider>
                              <v-card-actions>
                                <v-btn
                                  color="blue darken-1"
                                  text
                                  @click="dialog = false"
                                >
                                  Close
                                </v-btn>
                                <v-btn
                                  color="blue darken-1"
                                  text
                                  @click="dialog = false"
                                >
                                  Save
                                </v-btn>
                              </v-card-actions>
                            </v-card>
                          </v-dialog>
                        </v-col>
                      </v-row>
                    </v-card>
                    <div>
                      <v-btn color="primary" @click="e1 = 2">
                        Continue
                      </v-btn>

                      <v-btn text>
                        Cancel
                      </v-btn>
                    </div>
                  </v-stepper-content>

                  <v-stepper-content step="2">
                    <v-card class="mb-12" color="lighten-1" height="350px">
                      <v-radio-group v-model="predict_type" row>
                        <v-col cols="6">
                          <v-radio
                            label="ONLINE PREDICTION"
                            value="ONLINE_PREDICTION"
                          ></v-radio>
                        </v-col>
                        <v-col cols="6"
                          ><v-radio
                            label="BATCH PREDICTION"
                            value="BATCH_PREDICTION"
                          ></v-radio
                        ></v-col>
                      </v-radio-group>
                    </v-card>

                    <v-btn color="primary" @click="e1 = 3">
                      Continue
                    </v-btn>

                    <v-btn text>
                      Cancel
                    </v-btn>
                  </v-stepper-content>

                  <v-stepper-content step="3">
                    <v-card class="mb-12" color="lighten-1" height="350px">
                      <v-img
                        :src="
                          parse_base64_image
                            ? parse_base64_image
                            : image_select.url
                        "
                        height="auto"
                        width="150"
                      ></v-img>
                      <v-card-subtitle>
                        File name:
                        {{
                          image_select.blob ? image_select.blob : "file_upload"
                        }}
                      </v-card-subtitle>
                      <v-card-subtitle>
                        Predict type: {{ predict_type }}
                      </v-card-subtitle>
                      <v-card-title v-show="label !== ''">
                        Result: {{ label }} - {{ 100 * score }}%
                      </v-card-title>
                    </v-card>

                    <v-btn color="primary" @click="e1 = 1" v-show="e1 < 3">
                      Continue
                    </v-btn>
                    <v-alert type="error" v-show="errors !== ''">
                      {{ errors }}
                    </v-alert>
                    <v-btn color="primary" @click="submit" v-show="e1 === 3" :loading="submit_loading" :disabled="submit_loading">
                      Submit
                    </v-btn>
                    <v-btn text @click="cancel">
                      Cancel
                    </v-btn>
                  </v-stepper-content>
                </v-stepper-items>
              </v-stepper>
            </v-sheet>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
export default {
  data: () => ({
    drawer: null,
    e1: 1,
    file_url: [],
    is_uploaded: true,
    available_files: [],
    file_selected: {},
    image_select: "",
    dialog: false,
    parse_base64_image: "",
    predict_type: "ONLINE",
    score: 0,
    label: "",
    submit_loading: false,
    errors : ""
  }),
  methods: {
    onFilePicked(file) {
      return new Promise((resolve) => {
        if (file) {
          const fileReader = new FileReader();
          fileReader.addEventListener("load", () => {
            this.parse_base64_image = fileReader.result;
            resolve();
          });
          fileReader.readAsDataURL(file);
        }
      });
    },
    parse_image(file) {
      this.onFilePicked(file)
    },
    async submit() {
      if (this.image_select !== "") {
        this.is_uploaded = false;
      }
      // if (this.is_uploaded === true) await this.onFilePicked(this.file_url);
      let formData = new FormData();
      formData.append("file", this.file_url);
      formData.append("blob", this.image_select.blob_name);
      formData.append("is_uploaded", this.is_uploaded);
      formData.append("predict_type", this.predict_type);
      this.$axios
        .post("/predict", formData)
        .then((response) => {
          this.score = response.data.score;
          this.label = response.data.name;
        })
        .catch((error) => {
          this.errors = error.response.data.detail
        });
    },
    cancel() {
      this.file_url = [];
      this.is_uploaded = true;
      this.e1 = 1;
      this.file_selected = {};
      this.image_select = "";
      this.parse_base64_image = "";
      this.predict_type = "ONLINE";
      this.score = 0;
      this.label = "";
      this.errors = "";
    },
  },
  created() {
    this.$axios.get("/predict/sample").then((response) => {
      this.available_files = response.data;
      this.file_selected = this.available_files[0];
    });
  },

};
</script>

