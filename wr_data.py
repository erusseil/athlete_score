# Copyright 2025
# Author: Etienne Russeil
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np

#https://en.wikipedia.org/wiki/List_of_masters_world_records_in_road_running
marathon_age_femme = np.array([[30, 130],
                       [40, 144],
                       [45, 144],
                       [50, 151],
                       [59, 165],
                       [60, 169],
                       [65, 192],
                       [70, 208],
                       [76, 219],
                       [81, 252],
                       [85, 314],
                       [90, 407]])

marathon_age_homme = np.array([[17, 132],
                       [23, 121],
                       [41, 124],
                       [46, 129],
                       [50, 139],
                       [55, 144],
                       [60, 150],
                       [65, 162],
                       [71, 174],
                       [76, 185],
                       [80, 196],
                       [85, 239],
                       [90, 395]])

semi_age_homme = np.array([[17, 61],
                       [20, 57],
                       [40, 61],
                       [45, 61],
                       [50, 66],
                       [55, 70],
                       [60, 72],
                       [67, 76],
                       [71, 79],
                       [76, 89],
                       [81, 99],
                       [85, 111],
                       [90, 176]])

semi_age_femme = np.array([[23, 63],
                       [40, 68],
                       [45, 69],
                       [50, 75],
                       [55, 78],
                       [60, 82],
                       [65, 86],
                       [70, 97],
                       [76, 106],
                       [80, 124],
                       [85, 133],
                       [93, 289]])

sbd_poids_homme = np.array([[59, 669.5],
                         [66, 770.0],
                         [74, 843.0],
                         [83, 870.5],
                         [93, 917.5],
                         [105 ,940.5],
                         [120, 978.5],
                         [200, 1152.5],
                         [300, 1152.5]])

sbd_age_homme74 = np.array([[18, 766],
                            [26, 843],
                            [40, 730],
                            [50, 627],
                            [60, 559],
                            [70, 481]])


sbd_poids_femme = np.array([[47, 433.5],
                         [52, 481.0],
                         [57, 519.5],
                         [63, 557.5],
                         [69, 628.0],
                         [76, 616.0],
                         [84, 647.0],
                         [150, 735.5],
                         [220, 735.5]])

sbd_age_femme57 = np.array([[18, 420.0],
                            [23, 520],
                            [40, 444],
                            [53, 388],
                            [63, 326],
                            [73, 261]])

# Based on the absolute world record
SBD_percentages = np.array([470, 272.5, 410])/1152.5

# Based on rule of thumb
SBD_percentages = np.array([0.35, 0.25, 0.40])
