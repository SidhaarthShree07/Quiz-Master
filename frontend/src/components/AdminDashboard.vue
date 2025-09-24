<template>
  <div class="dashboard-page-wrapper">
    <div ref="vantaBg" class="vanta-bg"></div>
    <div class="admin-layout">
      <div class="admin-sidebar">
        <div class="view-as-student-wrapper">
          <button class="view-as-student-btn" @click="goToUserDashboard">View as Student</button>
        </div>
        <div class="admin-navbar-container">
          <nav class="admin-navbar">
            <ul>
              <li :class="{active: selected==='subjects'}" @click="selected='subjects'">
                <span class="icon"><font-awesome-icon :icon="['fas', 'book']" /></span>
                <span>Subjects</span>
              </li>
              <li :class="{active: selected==='quizzes'}" @click="selected='quizzes'">
                <span class="icon"><font-awesome-icon :icon="['fas', 'clipboard-list']" /></span>
                <span>Quizzes</span>
              </li>
              <li :class="{active: selected==='users'}" @click="selected='users'">
                <span class="icon"><font-awesome-icon :icon="['fas', 'users']" /></span>
                <span>Users</span>
              </li>
              <li :class="{active: selected==='stats'}" @click="router.push('/stats')">
                <span class="icon"><font-awesome-icon :icon="['fas', 'chart-bar']" /></span>
                <span>Stats</span>
              </li>
              <li :class="{active: selected==='logout'}" @click="handleLogout">
                <span class="icon"><font-awesome-icon :icon="['fas', 'right-from-bracket']" /></span>
                <span>Logout</span>
              </li>
            </ul>
          </nav>
        </div>
      </div>
      <div class="main-content-vertical">
        <div v-if="selected !== 'stats'" class="admin-searchbar">
          <input type="text" placeholder="Search..." class="search-input" v-model="searchQuery" />
          <span class="search-icon"><font-awesome-icon :icon="['fas', 'search']" /></span>
          <span v-if="searchQuery" class="search-clear" @click="clearSearch">
            <font-awesome-icon :icon="['fas', 'xmark']" />
          </span>
        </div>
        <div v-show="selected === 'subjects'" class="content-section">
          <template v-if="!showAddSubjectForm && !showAddChapterForm">
            <h1 class="dashboard-title">Subjects</h1>
            <p class="dashboard-sub">Manage your subjects here.</p>
          </template>
          <div v-if="showAddSubjectForm" class="add-subject-form-wrapper">
            <form class="add-subject-form" @submit.prevent="submitAddSubject">
              <div class="form-title">Add New Subject</div>
              <div class="form-group">
                <label for="subject-name">Name</label>
                <input id="subject-name" v-model="newSubject.name" required placeholder="Subject Name" />
              </div>
              <div class="form-group">
                <label for="subject-description">Description</label>
                <textarea id="subject-description" v-model="newSubject.description" placeholder="Description"></textarea>
              </div>
              <div class="form-group">
                <label for="subject-color">Color</label>
                <input id="subject-color" v-model="newSubject.color" placeholder="#4fd1c5 or color name" />
              </div>
              <div class="form-group">
                <label for="subject-image">Image File</label>
                <input id="subject-image" type="file" accept="image/*" @change="onSubjectImageChange" />
              </div>
              <div v-if="addSubjectError" class="form-error">{{ addSubjectError }}</div>
              <div class="form-actions">
                <button type="button" class="form-btn back" @click="closeAddSubjectForm">Back</button>
                <button type="submit" class="form-btn submit">Submit</button>
              </div>
            </form>
          </div>
          <div v-else-if="showEditSubjectForm" class="add-subject-form-wrapper">
            <form class="add-subject-form" @submit.prevent="submitEditSubject">
              <div class="form-title">Edit Subject</div>
              <div class="form-group">
                <label for="edit-subject-name">Name</label>
                <input id="edit-subject-name" v-model="editSubjectData.name" required :placeholder="editSubjectData.name" />
              </div>
              <div class="form-group">
                <label for="edit-subject-description">Description</label>
                <textarea id="edit-subject-description" v-model="editSubjectData.description" :placeholder="editSubjectData.description"></textarea>
              </div>
              <div class="form-group">
                <label for="edit-subject-color">Color</label>
                <input id="edit-subject-color" v-model="editSubjectData.color" :placeholder="editSubjectData.color" />
              </div>
              <div class="form-group">
                <label for="edit-subject-image">Image File</label>
                <input id="edit-subject-image" type="file" accept="image/*" @change="onEditSubjectImageChange" />
                <span v-if="editSubjectData.image_file_name" style="color: aliceblue;">Current: {{ editSubjectData.image_file_name }}</span>
              </div>
              <div v-if="editSubjectError" class="form-error">{{ editSubjectError }}</div>
              <div class="form-actions">
                <button type="button" class="form-btn back" @click="closeEditSubjectForm">Back</button>
                <button type="submit" class="form-btn submit">Submit</button>
              </div>
            </form>
          </div>
          <div v-else-if="showAddChapterForm" class="add-chapter-form-outer-wrapper">
            <form class="add-chapter-form" @submit.prevent="submitAddChapter">
              <div class="form-title">
                Add New Chapter to
                <span v-if="subjects && subjects.find(s => s.id === showAddChapterForm)">
                  {{ subjects.find(s => s.id === showAddChapterForm).name }}
                </span>
              </div>
              <div class="form-group">
                <label for="chapter-name">Name</label>
                <input id="chapter-name" v-model="newChapter.name" required placeholder="Chapter Name" />
              </div>
              <div class="form-group">
                <label for="chapter-description">Description</label>
                <textarea id="chapter-description" v-model="newChapter.description" placeholder="Description"></textarea>
              </div>
              <div class="form-group">
                <label for="chapter-image">Image File</label>
                <input id="chapter-image" type="file" accept="image/*" @change="onChapterImageChange" />
              </div>
              <div v-if="addChapterError" class="form-error">{{ addChapterError }}</div>
              <div class="form-actions">
                <button type="button" class="form-btn back" @click="closeAddChapterForm">Back</button>
                <button type="submit" class="form-btn submit">Submit</button>
              </div>
            </form>
          </div>
          <div v-else>
            <div v-if="loadingSubjects" class="subjects-loading">Loading...</div>
            <div v-else>
              <div v-if="!subjects || subjects.length === 0" class="no-subjects">No subjects found.</div>
              <div v-else class="subjects-grid">
                <div v-for="subject in filteredSubjects" :key="subject.id" class="subject-card">
                  <button class="card-x-btn" @click="openDeleteSubjectModal(subject)">×</button>
                  <div class="subject-card-header">{{ subject.name }}</div>
                  <div v-if="showAddChapterForm === subject.id" class="add-chapter-form-wrapper">
                    <form class="add-chapter-form" @submit.prevent="submitAddChapter">
                      <div class="form-title">Add New Chapter</div>
                      <div class="form-group">
                        <label for="chapter-name">Name</label>
                        <input id="chapter-name" v-model="newChapter.name" required placeholder="Chapter Name" />
                      </div>
                      <div class="form-group">
                        <label for="chapter-description">Description</label>
                        <textarea id="chapter-description" v-model="newChapter.description" placeholder="Description"></textarea>
                      </div>
                      <div class="form-group">
                        <label for="chapter-image">Image File</label>
                        <input id="chapter-image" type="file" accept="image/*" @change="onChapterImageChange" />
                      </div>
                      <div v-if="addChapterError" class="form-error">{{ addChapterError }}</div>
                      <div class="form-actions">
                        <button type="button" class="form-btn back" @click="closeAddChapterForm">Back</button>
                        <button type="submit" class="form-btn submit">Submit</button>
                      </div>
                    </form>
                  </div>
                  <div v-else>
                    <table class="subject-chapter-table">
                      <thead>
                        <tr>
                          <th>Chapter Name</th>
                          <th>No. of Quizzes</th>
                          <th>Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="chapter in subject.chapters" :key="chapter.id">
                          <td>{{ chapter.name }}</td>
                          <td>{{ chapter.quiz_count }}</td>
                          <td>
                            <button class="chapter-action-btn edit" @click="openEditChapterForm(subject, chapter)">Edit</button>
                            <button class="chapter-action-btn delete" @click="openDeleteChapterModal(subject, chapter)">Delete</button>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <div class="subject-card-footer" style="gap:1rem;">
                      <button class="add-chapter-btn" @click="openAddChapterForm(subject.id)">Add More Chapter</button>
                      <button class="add-chapter-btn edit" @click="openEditSubjectForm(subject)">Edit Subject</button>
                    </div>
                  </div>
                </div>
              </div>
              <div class="add-subject-btn-wrapper">
                <button class="add-subject-btn" @click="openAddSubjectForm">Add More Subjects</button>
              </div>
            </div>
          </div>
        </div>
        <div v-show="selected === 'quizzes'" class="content-section">
          <h1 class="dashboard-title">Quizzes</h1>
          <div v-if="showAddQuizForm">
            <div class="add-quiz-form-outer-wrapper">
              <form class="add-quiz-form" @submit.prevent="submitAddQuiz">
                <div class="form-title">Add New Quiz</div>
                <!-- ...existing add quiz form fields... -->
                <div class="form-group">
                  <label for="quiz-title">Title</label>
                  <input id="quiz-title" v-model="newQuiz.title" required placeholder="Quiz Title" />
                </div>
                <div class="form-group">
                  <label for="quiz-description">Description</label>
                  <textarea id="quiz-description" v-model="newQuiz.description" placeholder="Description"></textarea>
                </div>
                <div class="form-group">
                  <label for="quiz-subject">Subject</label>
                  <select id="quiz-subject" v-model="newQuiz.subjectId" @change="onQuizSubjectChange" class="styled-select">
                    <option value="" disabled selected>Select Subject</option>
                    <option v-for="subject in subjects" :key="subject.id" :value="subject.id">{{ subject.name }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label for="quiz-chapter">Chapter</label>
                  <select id="quiz-chapter" v-model="newQuiz.chapterId" :disabled="!newQuiz.subjectId || quizChapters.length === 0" class="styled-select">
                    <option value="" disabled selected>
                      {{ !newQuiz.subjectId ? 'Select subject first' : (quizChapters.length === 0 ? 'No chapters found for this subject' : 'Select Chapter') }}
                    </option>
                    <option v-for="chapter in quizChapters" :key="chapter.id" :value="chapter.id">{{ chapter.name }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label for="quiz-date">Date</label>
                  <input id="quiz-date" type="date" v-model="newQuiz.date" required />
                </div>
                <div class="form-group">
                  <label for="quiz-duration">Duration (minutes, 180 min max.)</label>
                  <input id="quiz-duration" type="number" v-model="newQuiz.duration" min="0" max="180" required style="width: 100%;" />
                </div>
                <div class="form-group form-group-marks-actions" style="display: flex; align-items: flex-start; gap: 1.2rem;">
                  <div style="flex:1; display:flex; flex-direction:column;">
                    <label for="quiz-cost">Cost</label>
                    <input id="quiz-cost" type="number" v-model="newQuiz.cost" min="0" required placeholder="Cost of the Quiz"  style="width: 24rem;"/>
                  </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1.3rem; height: 3rem;">
                  <button type="button" class="form-btn back" @click="closeAddQuizForm">Cancel</button>
                  <button type="submit" class="form-btn submit">Submit</button>
                  <div v-if="addQuizError" class="form-error" ><p>Failed</p></div>
                </div>
              </form>
            </div>
          </div>
          <div v-else-if="showEditQuizForm">
            <div class="add-quiz-form-outer-wrapper">
              <form class="add-quiz-form" @submit.prevent="submitEditQuiz">
                <div class="form-title">Edit Quiz</div>
                <div class="form-group">
                  <label for="edit-quiz-title">Title</label>
                  <input id="edit-quiz-title" v-model="editQuizData.title" :placeholder="editQuizData.title" />
                </div>
                <div class="form-group">
                  <label for="edit-quiz-description">Description</label>
                  <textarea id="edit-quiz-description" v-model="editQuizData.description" :placeholder="editQuizData.description"></textarea>
                </div>
                <div class="form-group">
                  <label for="edit-quiz-subject">Subject</label>
                  <select id="edit-quiz-subject" v-model="editQuizData.subjectId" class="styled-select">
                    <option v-for="subject in subjects" :key="subject.id" :value="subject.id">{{ subject.name }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label for="edit-quiz-chapter">Chapter</label>
                  <select id="edit-quiz-chapter" v-model="editQuizData.chapterId" class="styled-select">
                    <option v-for="chapter in quizChapters" :key="chapter.id" :value="chapter.id">{{ chapter.name }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label for="edit-quiz-date">Date</label>
                  <input id="edit-quiz-date" type="date" v-model="editQuizData.date" :placeholder="editQuizData.date" />
                </div>
                <div class="form-group">
                  <label for="edit-quiz-duration">Duration (minutes, 180 min max.)</label>
                  <input id="edit-quiz-duration" type="number" v-model="editQuizData.duration" min="0" max="180" :placeholder="editQuizData.duration" />
                </div>
                <div class="form-group form-group-marks-actions" style="display: flex; align-items: flex-start; gap: 1.2rem;">
                  <div style="flex:1; display:flex; flex-direction:column;">
                    <label for="edit-quiz-cost">Cost</label>
                    <input id="edit-quiz-cost" type="number" v-model="editQuizData.cost" min="0" :placeholder="editQuizData.cost" />
                  </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1.3rem; height: 3rem;">
                  <button type="button" class="form-btn back" @click="closeEditQuizForm">Cancel</button>
                  <button type="submit" class="form-btn submit">Submit</button>
                  <div v-if="editQuizError" class="form-error"><p>Failed</p></div>
                </div>
              </form>
            </div>
          </div>
          <div v-else-if="showAddQuestionForm" class="add-question-form-outer-wrapper">
          <form class="add-question-form" @submit.prevent="submitAddQuestion">
            <div class="form-title">Add New Question</div>
            <div class="form-group">
              <label>Question Type</label>
              <div style="display:flex; gap:1rem; margin-bottom: 0rem;">
                <label><input type="radio" value="text" v-model="newQuestion.questionType" @change="onquestionTypeChange('text')" /> Text</label>
                <label><input type="radio" value="image" v-model="newQuestion.questionType" @change="onquestionTypeChange('image')" /> Image</label>
              </div>
            </div>
            <div class="form-group" style="margin-bottom: 0rem;">
              <label for="question-title">Question Title</label>
              <input id="question-title" v-model="newQuestion.question_title" required placeholder="Question Title" />
            </div>
            <div class="form-group" v-if="newQuestion.questionType === 'text'" style="margin-bottom: 0rem;">
              <label for="question-statement">Question Statement (Text)</label>
              <textarea id="question-statement" v-model="newQuestion.question_statement" required placeholder="Question Statement"></textarea>
            </div>
            <div class="form-group" v-else style="margin-bottom: 0rem;">
              <label for="question-title-image">Question Statement (Image)</label>
              <input id="question-title-image" type="file" accept="image/*" @change="onQuestionTypeImageChange" required />
              <span v-if="newQuestion.question_statement">Selected: {{ newQuestion.question_statement }}</span>
            </div>
            <div class="form-group" style="margin-bottom: 0rem;">
              <label>Options</label>
              <div class="options-row">
                <input v-model="newQuestion.option_1" required placeholder="Option 1" />
                <input v-model="newQuestion.option_2" required placeholder="Option 2" />
              </div>
              <div class="options-row">
                <input v-model="newQuestion.option_3" required placeholder="Option 3" />
                <input v-model="newQuestion.option_4" required placeholder="Option 4" />
              </div>
            </div>
            <div class="form-group" style="margin-bottom: 0rem;">
              <label>Correct Option</label>
              <div class="correct-options-radios">
                <label class="radio-label">
                  <input type="radio" :value="1" v-model="newQuestion.correct_options" /> Option 1
                </label>
                <label class="radio-label">
                  <input type="radio" :value="2" v-model="newQuestion.correct_options" /> Option 2
                </label>
                <label class="radio-label">
                  <input type="radio" :value="3" v-model="newQuestion.correct_options" /> Option 3
                </label>
                <label class="radio-label">
                  <input type="radio" :value="4" v-model="newQuestion.correct_options" /> Option 4
                </label>
              </div>
            </div>
            <div class="form-group" style="margin-bottom: 0rem;">
              <label for="question-score">Score</label>
              <input id="question-score" type="number" v-model="newQuestion.score" min="1" required placeholder="Score for this question" />
            </div>
            <div class="form-actions" style="margin-bottom: 0rem;">
              <button type="button" class="form-btn back" @click="closeAddQuestionForm">Cancel</button>
              <button type="submit" class="form-btn submit">Submit</button>
            </div>
            <div v-if="addQuestionError" class="form-error">{{ addQuestionError }}</div>
          </form>
          </div>
          <div v-else-if="showEditQuestionForm" class="add-question-form-outer-wrapper">
            <form class="add-question-form" @submit.prevent="submitEditQuestion">
              <div class="form-title">Edit Question</div>
              <div class="form-group">
                <label>Question Type</label>
                <div style="display:flex; gap:1rem; margin-bottom: 0rem;">
                  <label><input type="radio" value="text" v-model="editQuestionData.questionType" @change="onEditquestionTypeChange('text')" /> Text</label>
                  <label><input type="radio" value="image" v-model="editQuestionData.questionType" @change="onEditquestionTypeChange('image')" /> Image</label>
                </div>
              </div>
              <div class="form-group" style="margin-bottom: 0rem;">
                <label for="edit-question-title">Question Title</label>
                <input id="edit-question-title" v-model="editQuestionData.question_title" required placeholder="Question Title" />
              </div>
              <div class="form-group" v-if="editQuestionData.questionType === 'text'" style="margin-bottom: 0rem;">
                <label for="edit-question-statement">Question Statement (Text)</label>
                <textarea id="edit-question-statement" v-model="editQuestionData.question_statement" required placeholder="Question Statement"></textarea>
              </div>
              <div class="form-group" v-else style="margin-bottom: 0rem;">
                <label for="edit-question-title-image">Question Text (Image)</label>
                <input id="edit-question-title-image" type="file" accept="image/*" @change="onEditQuestionTypeImageChange" required />
                <span v-if="editQuestionData.question_statement">Selected: {{ editQuestionData.question_statement }}</span>
              </div>
              <div class="form-group" style="margin-bottom: 0rem;">
                <label>Options</label>
                <div class="options-row">
                  <input v-model="editQuestionData.option_1" required placeholder="Option 1" />
                  <input v-model="editQuestionData.option_2" required placeholder="Option 2" />
                </div>
                <div class="options-row">
                  <input v-model="editQuestionData.option_3" required placeholder="Option 3" />
                  <input v-model="editQuestionData.option_4" required placeholder="Option 4" />
                </div>
              </div>
              <div class="form-group" style="margin-bottom: 0rem;">
                <label>Correct Option</label>
                <div class="correct-options-radios">
                  <label class="radio-label">
                    <input type="radio" :value="1" v-model="editQuestionData.correct_options" /> Option 1
                  </label>
                  <label class="radio-label">
                    <input type="radio" :value="2" v-model="editQuestionData.correct_options" /> Option 2
                  </label>
                  <label class="radio-label">
                    <input type="radio" :value="3" v-model="editQuestionData.correct_options" /> Option 3
                  </label>
                  <label class="radio-label">
                    <input type="radio" :value="4" v-model="editQuestionData.correct_options" /> Option 4
                  </label>
                </div>
                <small>Select only one correct option</small>
              </div>
              <div class="form-group" style="margin-bottom: 0rem;">
                <label for="edit-question-score">Score</label>
                <input id="edit-question-score" type="number" v-model="editQuestionData.score" min="1" required placeholder="Score for this question" />
              </div>
              <div class="form-actions" style="margin-bottom: 0rem;">
                <button type="button" class="form-btn back" @click="closeEditQuestionForm">Cancel</button>
                <button type="submit" class="form-btn submit">Submit</button>
              </div>
              <div v-if="editQuestionError" class="form-error">{{ editQuestionError }}</div>
            </form>
          </div>
          <div v-else>
            <div v-if="loadingQuizzes" class="subjects-loading">Loading...</div>
            <div v-if="quizzes.length === 0" class="no-subjects">No quizzes found.</div>
            <div v-else class="subjects-grid">
              <div v-for="quiz in filteredQuizzes" :key="quiz.id" class="subject-card">
                <button class="card-x-btn" @click="openDeleteQuizModal(quiz)">×</button>
                <div class="subject-card-header">
                  {{ quiz.name }} <span v-if="quiz.chapter_name">({{ quiz.chapter_name }})</span>
                </div>
                <table class="subject-chapter-table">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Question Title</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(question, idx) in quiz.questions" :key="question.id">
                      <td>{{ idx + 1 }}</td>
                      <td>{{ question.question_title }}</td>
                      <td>
                        <button class="chapter-action-btn edit" @click="openEditQuestionModal(quiz, question)">Edit</button>
                        <button class="chapter-action-btn delete" @click="openDeleteQuestionModal(quiz, question)">Delete</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <div class="subject-card-footer" style="gap:1rem;">
                  <button class="add-chapter-btn" @click="() => openAddQuestionForm(quiz)">Add Question</button>
                  <button class="add-chapter-btn edit" @click="() => openEditQuizForm(quiz)">Edit Quiz</button>
                </div>
              </div>
            </div>
            <div class="add-subject-btn-wrapper" style="margin-top:2.5rem;">
              <button class="add-quiz-btn" @click="openAddQuizForm">Add Quiz</button>
            </div>
          </div>
        </div>
        <div v-show="selected === 'users'" class="content-section">
          <h1 class="dashboard-title">Users</h1>
          <p class="dashboard-sub">View user statistics here.</p>
          <!-- Users (was Statistics) content -->
          <div class="stats-table-wrapper">
            <table class="stats-table">
              <thead>
                <tr>
                  <th>Sr No.</th>
                  <th>Username</th>
                  <th>Quizzes Booked</th>
                  <th>Last Interaction</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(user, idx) in filteredStatsUsers" :key="user.id">
                  <td>{{ idx + 1 }}</td>
                  <td>{{ user.username }}</td>
                  <td>
                    <span v-if="user.bookedQuizzes.length === 0">None</span>
                    <span v-else>{{ user.bookedQuizzes.join(', ') }}</span>
                  </td>
                  <td>
                    <span v-if="user.last_interaction">{{ formatDateTime(user.last_interaction) }}</span>
                    <span v-else>Hasn't interacted yet</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <!-- Stats tab now navigates to /stats route and uses StatsView component -->
        <!-- Add Question Modal: overlays/hides other content in main-content-vertical -->
      </div>
    </div>
    <div v-if="showDeleteSubjectModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-title">Confirm Delete</div>
        <div class="modal-body">
          Are you sure you want to delete the subject <b>{{ subjectToDelete?.name }}</b>?
        </div>
        <div class="modal-actions">
          <button class="modal-btn cancel" @click="closeDeleteSubjectModal">Cancel</button>
          <button class="modal-btn delete" @click="confirmDeleteSubject">Delete</button>
        </div>
      </div>
    </div>
    <div v-if="showDeleteChapterModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-title">Confirm Delete</div>
        <div class="modal-body">
          Are you sure you want to delete the chapter <b>{{ chapterToDelete?.name }}</b>?
        </div>
        <div class="modal-actions">
          <button class="modal-btn cancel" @click="closeDeleteChapterModal">Cancel</button>
          <button class="modal-btn delete" @click="confirmDeleteChapter">Delete</button>
        </div>
      </div>
    </div>
    <div v-if="showDeleteQuizModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-title">Confirm Delete</div>
        <div class="modal-body">
          Are you sure you want to delete the quiz <b>{{ quizToDelete?.name }}</b>?
        </div>
        <div class="modal-actions">
          <button class="modal-btn cancel" @click="closeDeleteQuizModal">Cancel</button>
          <button class="modal-btn delete" @click="confirmDeleteQuiz">Delete</button>
        </div>
      </div>
    </div>
     <!-- Delete Question Modal -->
    <div v-if="showDeleteQuestionModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-title">Confirm Delete</div>
        <div class="modal-body">
          Are you sure you want to delete this question?<br>
          <b>{{ questionToDelete?.question_title }}</b>
        </div>
        <div class="modal-actions">
          <button class="modal-btn cancel" @click="closeDeleteQuestionModal">Cancel</button>
          <button class="modal-btn delete" @click="confirmDeleteQuestion">Delete</button>
        </div>
        <div v-if="deleteQuestionError" class="form-error">{{ deleteQuestionError }}</div>
      </div>
    </div>
    <!-- Edit Chapter Modal -->
    <div v-if="showEditChapterForm" class="edit-chapter-form-outer-wrapper">
      <form v-if="!editChapterLoading" class="add-chapter-form" @submit.prevent="submitEditChapter" style="background: rgba(30, 30, 30, 1);">
        <div class="form-title">Edit Chapter</div>
        <div class="form-group">
          <label for="edit-chapter-name">Name</label>
          <input id="edit-chapter-name" v-model="editChapterData.name" required placeholder="Chapter Name" />
        </div>
        <div class="form-group">
          <label for="edit-chapter-description">Description</label>
          <textarea id="edit-chapter-description" v-model="editChapterData.description" placeholder="Description"></textarea>
        </div>
        <div class="form-group">
          <label for="edit-chapter-image">Image File</label>
          <input id="edit-chapter-image" type="file" accept="image/*" @change="onEditChapterImageChange" />
          <span v-if="editChapterData.image_file_name" style="color: aliceblue;">Current: {{ editChapterData.image_file_name }}</span>
        </div>
        <div v-if="editChapterError" class="form-error">{{ editChapterError }}</div>
        <div class="form-actions">
          <button type="button" class="form-btn back" @click="closeEditChapterForm">Cancel</button>
          <button type="submit" class="form-btn submit">Confirm</button>
        </div>
      </form>
      <div v-else class="form-title" style="text-align:center; color:#4fd1c5;">Loading chapter data...</div>
    </div>
  </div>
</template>

<script setup>
const goToUserDashboard = () => {
  router.push('/dashboard')
}
// Edit Quiz modal state
const showEditQuizForm = ref(false)
const editQuizData = ref({
  id: '',
  title: '',
  description: '',
  subjectId: '',
  chapterId: '',
  date: '',
  duration: '',
  cost: ''
})
const editQuizError = ref('')

const openEditQuizForm = (quiz) => {
  showEditQuizForm.value = true
  editQuizError.value = ''
  editQuizData.value = {
    id: quiz.id,
    title: quiz.name || quiz.title || '',
    description: quiz.remarks || '',
    subjectId: quiz.subject_id || '',
    chapterId: quiz.chapter_id || '',
    date: quiz.date || '',
    duration: quiz.duration || '',
    cost: quiz.cost || ''
  }
  updateEditQuizChapters()
}

const updateEditQuizChapters = () => {
  const subject = subjects.value.find(s => s.id === editQuizData.value.subjectId)
  quizChapters.value = subject ? subject.chapters : []
}

watch(() => editQuizData.value.subjectId, () => {
  updateEditQuizChapters()
  // Reset chapterId if not in new subject
  if (!quizChapters.value.find(c => c.id === editQuizData.value.chapterId)) {
    editQuizData.value.chapterId = ''
  }
})

const closeEditQuizForm = () => {
  showEditQuizForm.value = false
  editQuizError.value = ''
}

const submitEditQuiz = async () => {
  editQuizError.value = ''
  try {
    const formData = new FormData()
    // Only append fields that are not empty (allow partial update)
    if (editQuizData.value.title) formData.append('title', editQuizData.value.title)
    if (editQuizData.value.description) formData.append('description', editQuizData.value.description)
    if (editQuizData.value.subjectId) formData.append('subject_id', editQuizData.value.subjectId)
    if (editQuizData.value.chapterId) formData.append('chapter_id', editQuizData.value.chapterId)
    if (editQuizData.value.date) formData.append('date', editQuizData.value.date)
    if (editQuizData.value.duration) formData.append('duration', editQuizData.value.duration)
    if (editQuizData.value.cost) formData.append('cost', editQuizData.value.cost)
    await axios.put(`http://localhost:5000/api/admin/quizzes/${editQuizData.value.id}`, formData, { withCredentials: true })
    showEditQuizForm.value = false
    // Optionally refresh quizzes list here
  } catch (e) {
    editQuizError.value = e?.response?.data?.message || 'Failed to update quiz.'
  }
}

// Edit Question modal state
const showEditQuestionForm = ref(false)
const editQuestionQuiz = ref(null)
const editQuestionData = ref({
  id: '',
  questionType: 'text',
  question_title: '',
  question_statement_image: null,
  question_statement: '',
  option_1: '',
  option_2: '',
  option_3: '',
  option_4: '',
  correct_options: [],
  score: 1
})
const editQuestionError = ref('')

const openEditQuestionModal = (quiz, question) => {
showEditQuestionForm.value = true
editQuestionQuiz.value = quiz
editQuestionError.value = ''
// Fetch question details from backend
axios.get(`http://localhost:5000/api/admin/questions/${question.id}`, { withCredentials: true })
  .then(res => {
    const q = res.data
    editQuestionData.value = {
      id: q.id,
      questionType: q.question_type || 'text',
      question_title: q.question_title || '',
      question_statement_image: null,
      question_statement: q.question_statement || '',
      option_1: q.option_1 || '',
      option_2: q.option_2 || '',
      option_3: q.option_3 || '',
      option_4: q.option_4 || '',
      correct_options: Array.isArray(q.correct_options) ? q.correct_options : (q.correct_options ? JSON.parse(q.correct_options) : []),
      score: q.score || 1
    }
    // Ensure correct_options is a single value for radio selection
    if (Array.isArray(editQuestionData.value.correct_options) && editQuestionData.value.correct_options.length > 0) {
      editQuestionData.value.correct_options = editQuestionData.value.correct_options[0];
    }
  })
  .catch(() => {
    // fallback to passed question if fetch fails
    editQuestionData.value = {
      id: question.id,
      questionType: question.question_type || 'text',
      question_title: question.question_title || '',
      question_statement_image: null,
      question_statement: question.question_statement || '',
      option_1: question.option_1 || '',
      option_2: question.option_2 || '',
      option_3: question.option_3 || '',
      option_4: question.option_4 || '',
      correct_options: Array.isArray(question.correct_options) ? question.correct_options : (question.correct_options ? JSON.parse(question.correct_options) : []),
      score: question.score || 1
    }
    // Ensure correct_options is a single value for radio selection
    if (Array.isArray(editQuestionData.value.correct_options) && editQuestionData.value.correct_options.length > 0) {
      editQuestionData.value.correct_options = editQuestionData.value.correct_options[0];
    }
  })
}

const closeEditQuestionForm = () => {
  showEditQuestionForm.value = false
  editQuestionQuiz.value = null
  editQuestionError.value = ''
}

const onEditquestionTypeChange = (type) => {
  editQuestionData.value.questionType = type
  editQuestionData.value.question_statement = ''
  editQuestionData.value.question_statement_image = null
}

const onEditQuestionTypeImageChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    editQuestionData.value.question_statement_image = file
    editQuestionData.value.question_statement = file.name
  }
}

const submitEditQuestion = async () => {
  editQuestionError.value = ''
  if (!editQuestionQuiz.value || !editQuestionData.value.id) return
  try {
    const formData = new FormData()
    if (editQuestionData.value.questionType) formData.append('question_type', editQuestionData.value.questionType)
    if (editQuestionData.value.question_title) formData.append('question_title', editQuestionData.value.question_title)
    if (editQuestionData.value.questionType === 'image' && editQuestionData.value.question_statement_image) {
      formData.append('question_statement_image', editQuestionData.value.question_statement_image)
    }
    if (editQuestionData.value.question_statement) formData.append('question_statement', editQuestionData.value.question_statement)
    if (editQuestionData.value.option_1) formData.append('option_1', editQuestionData.value.option_1)
    if (editQuestionData.value.option_2) formData.append('option_2', editQuestionData.value.option_2)
    if (editQuestionData.value.option_3) formData.append('option_3', editQuestionData.value.option_3)
    if (editQuestionData.value.option_4) formData.append('option_4', editQuestionData.value.option_4)
    if (editQuestionData.value.correct_options) formData.append('correct_options', JSON.stringify(editQuestionData.value.correct_options))
    if (editQuestionData.value.score) formData.append('score', editQuestionData.value.score)
    await axios.put(`http://localhost:5000/api/admin/questions/${editQuestionData.value.id}`, formData, { withCredentials: true })
    showEditQuestionForm.value = false
    editQuestionQuiz.value = null
    // Optionally refresh quizzes/questions list here
  } catch (e) {
    editQuestionError.value = e?.response?.data?.message || 'Failed to update question.'
  }
}

import { ref, onMounted, onBeforeUnmount, nextTick, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

const username = ref('')
const router = useRouter()
const vantaBg = ref(null)
let vantaEffect = null
const selected = ref('subjects')
const subjects = ref([])
const loadingSubjects = ref(false)
const showAddSubjectForm = ref(false)
const newSubject = ref({ name: '', description: '', color: '', image_file_name: '' })
const addSubjectError = ref('')
const showAddChapterForm = ref(null) // subject id or null
const newChapter = ref({ name: '', description: '', image_file_name: '' })
const addChapterError = ref('')
const showDeleteSubjectModal = ref(false)
const subjectToDelete = ref(null)
const showDeleteChapterModal = ref(false)
const chapterToDelete = ref(null)
const subjectOfChapterToDelete = ref(null)
const showEditChapterForm = ref(false) // true if modal open
const editChapterData = ref({ name: '', description: '', image_file_name: '' })
const editChapterError = ref('')
const subjectOfChapterToEdit = ref(null)
const editChapterLoading = ref(false)
const editChapterId = ref(null)
const showAddQuizForm = ref(false)
const newQuiz = ref({
  title: '',
  description: '',
  subjectId: '',
  chapterId: '',
  date: '',
  duration: 0,
  totalMarks: ''
})
const addQuizError = ref('')
const quizChapters = ref([])

// Quizzes state
const quizzes = ref([])
const loadingQuizzes = ref(false)
const showDeleteQuizModal = ref(false)
const quizToDelete = ref(null)

// Delete Question modal state
const showDeleteQuestionModal = ref(false)
const questionToDelete = ref(null)
const quizOfQuestionToDelete = ref(null)
const deleteQuestionError = ref('')

const openDeleteQuestionModal = (quiz, question) => {
  showDeleteQuestionModal.value = true
  questionToDelete.value = question
  quizOfQuestionToDelete.value = quiz
  deleteQuestionError.value = ''
}
const closeDeleteQuestionModal = () => {
  showDeleteQuestionModal.value = false
  questionToDelete.value = null
  quizOfQuestionToDelete.value = null
  deleteQuestionError.value = ''
}
const confirmDeleteQuestion = async () => {
  if (!questionToDelete.value) return
  try {
    await axios.delete(`http://localhost:5000/api/admin/questions/${questionToDelete.value.id}`, { withCredentials: true })
    showDeleteQuestionModal.value = false
    questionToDelete.value = null
    quizOfQuestionToDelete.value = null
    fetchQuizzes()
  } catch (e) {
    deleteQuestionError.value = e?.response?.data?.message || 'Failed to delete question.'
  }
}

// Add Question modal state
const showAddQuestionForm = ref(false)
const addQuestionQuiz = ref(null)
const newQuestion = ref({
  questionType: 'text', // 'text' or 'image'
  question_title: '',
  question_statement_image: null,
  question_statement: '',
  option_1: '',
  option_2: '',
  option_3: '',
  option_4: '',
  correct_options: [], // array of option numbers
  score: 1
})
const addQuestionError = ref('')

const fetchSubjects = async () => {
  loadingSubjects.value = true
  try {
    const res = await axios.get('http://localhost:5000/api/admin/subjects', { withCredentials: true })
    subjects.value = res.data
  } catch {
    subjects.value = []
  } finally {
    loadingSubjects.value = false
  }
}

const fetchQuizzes = async () => {
  loadingQuizzes.value = true
  try {
    const res = await axios.get('http://localhost:5000/api/admin/quizzes', { withCredentials: true })
    quizzes.value = res.data
  } catch {
    quizzes.value = []
  } finally {
    loadingQuizzes.value = false
  }
}

async function fetchStatsUsers() {
  try {
    // Backend API already returns users with bookedQuizzes and last_interaction
    const res = await axios.get('http://localhost:5000/api/admin/stats/users', { withCredentials: true })
    statsUsers.value = res.data;
  } catch (e) {
    statsUsers.value = [];
  }
}

onMounted(async () => {
  await nextTick();
  await fetchStatsUsers();
  // Vanta background
  const tryInit = () => {
    if (window.VANTA && window.VANTA.TOPOLOGY && vantaBg.value) {
      if (vantaEffect) vantaEffect.destroy();
      vantaEffect = window.VANTA.TOPOLOGY({
        el: vantaBg.value,
        mouseControls: true,
        touchControls: true,
        gyroControls: false,
        minHeight: 800.0,
        minWidth: 800.0,
        scale: 1.0,
        scaleMobile: 1.0,
        backgroundColor: 0x0f111a,
        color: 0x4fd1c5,
        spacing: 40,
        points: 12,
        maxDistance: 25
      });
    } else {
      setTimeout(tryInit, 100);
    }
  };
  tryInit();
  try {
    const res = await axios.get('http://localhost:5000/api/user/dashboard', { withCredentials: true })
    username.value = res.data.username
  } catch {
    router.push('/login')
  }
  await fetchSubjects();
  await fetchQuizzes();
})
onBeforeUnmount(() => {
  if (vantaEffect) vantaEffect.destroy();
})

const searchQuery = ref('')
function clearSearch() {
  searchQuery.value = ''
}
// Subjects tab search logic
const filteredSubjects = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return subjects.value
  // Match subject name
  const subjectMatches = subjects.value.filter(sub => sub.name.toLowerCase().includes(query))
  if (subjectMatches.length > 0) return subjectMatches
  // Match chapters
  return subjects.value
    .map(sub => {
      const matchingChapters = sub.chapters?.filter(chap => chap.name.toLowerCase().includes(query)) || []
      if (matchingChapters.length > 0) {
        return { ...sub, chapters: matchingChapters }
      }
      return null
    })
    .filter(Boolean)
})
// Quizzes tab search logic
const filteredQuizzes = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return quizzes.value
  // Match quiz name
  const quizMatches = quizzes.value.filter(q => q.name.toLowerCase().includes(query))
  if (quizMatches.length > 0) return quizMatches
  // Match questions
  return quizzes.value
    .map(q => {
      const matchingQuestions = q.questions?.filter(ques => ques.question_title?.toLowerCase().includes(query)) || []
      if (matchingQuestions.length > 0) {
        return { ...q, questions: matchingQuestions }
      }
      return null
    })
    .filter(Boolean)
})
// Stats tab search logic
const filteredStatsUsers = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return statsUsers.value
  return statsUsers.value.filter(u => {
    // Match username or any booked quiz name
    if (u.username?.toLowerCase().includes(query)) return true
    if (Array.isArray(u.bookedQuizzes) && u.bookedQuizzes.some(qn => qn.toLowerCase().includes(query))) return true
    return false
  })
})

onMounted(async () => {
  await nextTick();
  await fetchStatsUsers();
  // Vanta background
  const tryInit = () => {
    if (window.VANTA && window.VANTA.TOPOLOGY && vantaBg.value) {
      if (vantaEffect) vantaEffect.destroy();
      vantaEffect = window.VANTA.TOPOLOGY({
        el: vantaBg.value,
        mouseControls: true,
        touchControls: true,
        gyroControls: false,
        minHeight: 800.0,
        minWidth: 800.0,
        scale: 1.0,
        scaleMobile: 1.0,
        backgroundColor: 0x0f111a,
        color: 0x4fd1c5,
        spacing: 40,
        points: 12,
        maxDistance: 25
      });
    } else {
      setTimeout(tryInit, 100);
    }
  };
  tryInit();
  try {
    const res = await axios.get('http://localhost:5000/api/user/dashboard', { withCredentials: true })
    username.value = res.data.username
  } catch {
    router.push('/login')
  }
  await fetchSubjects();
  await fetchQuizzes();
})
onBeforeUnmount(() => {
  if (vantaEffect) vantaEffect.destroy();
})

const handleLogout = async () => {
  try {
    await axios.post('http://localhost:5000/api/auth/logout-session-only', {}, { withCredentials: true })
    window.location.href = '/'
  } catch (e) {
    window.location.href = '/'
  }
}

const statsUsers = ref([])

function formatDateTime(dt) {
  if (!dt) return '';
  try {
    const d = typeof dt === 'string' ? new Date(dt) : dt;
    if (isNaN(d.getTime())) return dt;
    return d.toLocaleString();
  } catch {
    return dt;
  }
}

const openAddSubjectForm = () => {
  showAddSubjectForm.value = true
  addSubjectError.value = ''
  newSubject.value = { name: '', description: '', color: '', image_file_name: '' }
}
const closeAddSubjectForm = () => {
  showAddSubjectForm.value = false
  fetchSubjects()
  fetchQuizzes()
  addSubjectError.value = ''
}
const submitAddSubject = async () => {
  addSubjectError.value = ''
  try {
    const formData = new FormData()
    formData.append('name', newSubject.value.name)
    formData.append('description', newSubject.value.description)
    formData.append('color', newSubject.value.color)
    if (newSubject.value.imageFile) {
      formData.append('image', newSubject.value.imageFile)
    }
    await axios.post('http://localhost:5000/api/admin/subjects', formData, { withCredentials: true })
    showAddSubjectForm.value = false
    fetchSubjects()
  } catch (e) {
    addSubjectError.value = e?.response?.data?.message || 'Failed to add subject.'
  }
}
const onSubjectImageChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    newSubject.value.imageFile = file
    newSubject.value.image_file_name = file.name
  }
}
const openAddChapterForm = (subjectId) => {
  showAddChapterForm.value = subjectId
  addChapterError.value = ''
  newChapter.value = { name: '', description: '', image_file_name: '' }
}
const closeAddChapterForm = () => {
  showAddChapterForm.value = null
    fetchSubjects()
    fetchQuizzes()
  addChapterError.value = ''
}
const submitAddChapter = async () => {
  addChapterError.value = ''
  try {
    const formData = new FormData()
    formData.append('name', newChapter.value.name)
    formData.append('description', newChapter.value.description)
    if (newChapter.value.imageFile) {
      formData.append('image', newChapter.value.imageFile)
    }
    await axios.post(`http://localhost:5000/api/admin/subjects/${showAddChapterForm.value}/chapters`, formData, { withCredentials: true })
    showAddChapterForm.value = null
    fetchSubjects()
  } catch (e) {
    addChapterError.value = e?.response?.data?.message || 'Failed to add chapter.'
  }
}
const onChapterImageChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    newChapter.value.imageFile = file
    newChapter.value.image_file_name = file.name
  }
}
const openDeleteSubjectModal = (subject) => {
  subjectToDelete.value = subject
  showDeleteSubjectModal.value = true
}
const closeDeleteSubjectModal = () => {
  showDeleteSubjectModal.value = false
  subjectToDelete.value = null
}
const confirmDeleteSubject = async () => {
  if (!subjectToDelete.value) return
  try {
    await axios.delete(`http://localhost:5000/api/admin/subjects/${subjectToDelete.value.id}`, { withCredentials: true })
    showDeleteSubjectModal.value = false
    subjectToDelete.value = null
    fetchSubjects()
  } catch (e) {
    // Optionally show error
    showDeleteSubjectModal.value = false
    subjectToDelete.value = null
  }
}

// Edit Subject modal state
const showEditSubjectForm = ref(false)
const editSubjectData = ref({ name: '', description: '', color: '', image_file_name: '', imageFile: null })
const editSubjectError = ref('')
const editSubjectId = ref(null)

const openEditSubjectForm = async (subject) => {
  editSubjectError.value = ''
  showEditSubjectForm.value = true
  editSubjectId.value = subject.id
  try {
    const res = await axios.get(`http://localhost:5000/api/admin/subjects/${subject.id}`, { withCredentials: true })
    editSubjectData.value = {
      name: res.data.name,
      description: res.data.description || '',
      color: res.data.color || '',
      image_file_name: res.data.image_file_name || '',
      imageFile: null
    }
  } catch (e) {
    editSubjectError.value = 'Failed to fetch subject data.'
  }
}
const closeEditSubjectForm = () => {
  showEditSubjectForm.value = false
    fetchSubjects()
    fetchQuizzes()
  editSubjectId.value = null
  editSubjectError.value = ''
  editSubjectData.value = { name: '', description: '', color: '', image_file_name: '', imageFile: null }
}
const onEditSubjectImageChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    editSubjectData.value.imageFile = file
    editSubjectData.value.image_file_name = file.name
  }
}
const submitEditSubject = async () => {
  editSubjectError.value = ''
  try {
    const formData = new FormData()
    if (editSubjectData.value.name) formData.append('name', editSubjectData.value.name)
    if (editSubjectData.value.description) formData.append('description', editSubjectData.value.description)
    if (editSubjectData.value.color) formData.append('color', editSubjectData.value.color)
    if (editSubjectData.value.imageFile) formData.append('image', editSubjectData.value.imageFile)
    await axios.put(`http://localhost:5000/api/admin/subjects/${editSubjectId.value}`, formData, { withCredentials: true })
    showEditSubjectForm.value = false
    // Optionally refresh subjects list here
    await fetchSubjects()
  } catch (e) {
    editSubjectError.value = e?.response?.data?.message || 'Failed to update subject.'
  }
}

const openDeleteChapterModal = (subject, chapter) => {
  subjectOfChapterToDelete.value = subject
  chapterToDelete.value = chapter
  showDeleteChapterModal.value = true
}
const closeDeleteChapterModal = () => {
  showDeleteChapterModal.value = false
  chapterToDelete.value = null
  subjectOfChapterToDelete.value = null
}
const confirmDeleteChapter = async () => {
  if (!chapterToDelete.value || !subjectOfChapterToDelete.value) return
  try {
    await axios.delete(`http://localhost:5000/api/admin/subjects/${subjectOfChapterToDelete.value.id}/chapters/${chapterToDelete.value.id}`, { withCredentials: true })
    showDeleteChapterModal.value = false
    chapterToDelete.value = null
    subjectOfChapterToDelete.value = null
    fetchSubjects()
  } catch (e) {
    showDeleteChapterModal.value = false
    chapterToDelete.value = null
    subjectOfChapterToDelete.value = null
  }
}
const openEditChapterForm = async (subject, chapter) => {
  editChapterError.value = ''
  editChapterLoading.value = true
  showEditChapterForm.value = true
  editChapterId.value = chapter.id
  try {
    const res = await axios.get(`http://localhost:5000/api/admin/subjects/${subject.id}/chapters/${chapter.id}`, { withCredentials: true })
    editChapterData.value = {
      name: res.data.name,
      description: res.data.description,
      image_file_name: res.data.image_file_name || '',
      imageFile: null
    }
    subjectOfChapterToEdit.value = subject
    editChapterLoading.value = false
  } catch (e) {
    editChapterError.value = 'Failed to fetch chapter data.'
    editChapterLoading.value = false
  }
}
const closeEditChapterForm = () => {
  showEditChapterForm.value = false
  editChapterId.value = null
  editChapterError.value = ''
  editChapterData.value = { name: '', description: '', image_file_name: '' }
  subjectOfChapterToEdit.value = null
  editChapterLoading.value = false
}
const onEditChapterImageChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    editChapterData.value.imageFile = file
    editChapterData.value.image_file_name = file.name
  }
}
const submitEditChapter = async () => {
  editChapterError.value = ''
  try {
    const formData = new FormData()
    formData.append('name', editChapterData.value.name)
    formData.append('description', editChapterData.value.description)
    if (editChapterData.value.imageFile) {
      formData.append('image', editChapterData.value.imageFile)
    }
    await axios.put(`http://localhost:5000/api/admin/subjects/${subjectOfChapterToEdit.value.id}/chapters/${editChapterId.value}`, formData, { withCredentials: true })
    closeEditChapterForm()
    fetchQuizzes()
    fetchSubjects()
  } catch (e) {
    editChapterError.value = e?.response?.data?.message || 'Failed to update chapter.'
  }
}
const openAddQuizForm = () => {
  showAddQuizForm.value = true
  addQuizError.value = ''
  newQuiz.value = {
    title: '',
    description: '',
    subjectId: '',
    chapterId: '',
    date: '',
    duration: 0,
    totalMarks: ''
  }
  quizChapters.value = []
}
const closeAddQuizForm = () => {
  showAddQuizForm.value = false
    fetchQuizzes()
    fetchSubjects()
  addQuizError.value = ''
}
const onQuizSubjectChange = () => {
  newQuiz.value.chapterId = ''
  if (!newQuiz.value.subjectId) {
    quizChapters.value = []
    return
  }
  const subject = subjects.value.find(s => s.id === newQuiz.value.subjectId)
  quizChapters.value = subject ? subject.chapters : []
}
const submitAddQuiz = async () => {
  addQuizError.value = ''
  try {
    const formData = new FormData()
    if (newQuiz.value.title) formData.append('title', newQuiz.value.title)
    if (newQuiz.value.description) formData.append('description', newQuiz.value.description)
    if (newQuiz.value.subjectId) formData.append('subject_id', newQuiz.value.subjectId)
    if (newQuiz.value.chapterId) formData.append('chapter_id', newQuiz.value.chapterId)
    if (newQuiz.value.date) formData.append('date', newQuiz.value.date)
    if (newQuiz.value.duration) formData.append('duration', newQuiz.value.duration)
    if (newQuiz.value.cost) formData.append('cost', newQuiz.value.cost)
    await axios.post('http://localhost:5000/api/admin/quizzes', formData, { withCredentials: true })
    showAddQuizForm.value = false
    await fetchQuizzes() // Refresh quizzes section after adding
    await fetchSubjects() // Optionally refresh subjects if needed
  } catch (e) {
    addQuizError.value = e?.response?.data?.message || 'Failed to add quiz.'
  }
}
const openDeleteQuizModal = (quiz) => {
  quizToDelete.value = quiz
  showDeleteQuizModal.value = true
}
const closeDeleteQuizModal = () => {
  showDeleteQuizModal.value = false
  quizToDelete.value = null
}
const confirmDeleteQuiz = async () => {
  if (!quizToDelete.value) return
  try {
    await axios.delete(`http://localhost:5000/api/admin/quizzes/${quizToDelete.value.id}`, { withCredentials: true })
    showDeleteQuizModal.value = false
    quizToDelete.value = null
    fetchQuizzes()
  } catch {
    showDeleteQuizModal.value = false
    quizToDelete.value = null
  }
}
const openAddQuestionForm = (quiz) => {
  console.log('Add Question button clicked for quiz:', quiz);
  showAddQuestionForm.value = true;
  addQuestionQuiz.value = quiz;
  addQuestionError.value = '';
  newQuestion.value = {
    questionType: 'text',
    question_title: '',
    question_statement_image: null,
    question_statement: '',
    option_1: '',
    option_2: '',
    option_3: '',
    option_4: '',
    correct_options: [],
    score: 1
  };
  console.log('showAddQuestionForm:', showAddQuestionForm.value);
  console.log('addQuestionQuiz:', addQuestionQuiz.value);
}

import { watch } from 'vue';
watch(showAddQuestionForm, (val) => {
  console.log('showAddQuestionForm changed:', val);
  if (val) {
    console.log('Add Question modal should be visible now.');
  } else {
    console.log('Add Question modal closed.');
  }
});
const closeAddQuestionForm = () => {
  showAddQuestionForm.value = false
    fetchQuizzes()
    fetchSubjects()
  addQuestionQuiz.value = null
  addQuestionError.value = ''
}
const onquestionTypeChange = (type) => {
  newQuestion.value.questionType = type
  newQuestion.value.question_statement = ''
  newQuestion.value.question_statement_image = null
}
const onQuestionTypeImageChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    newQuestion.value.question_statement_image = file
    newQuestion.value.question_statement = file.name
  }
}
const submitAddQuestion = async () => {
  addQuestionError.value = ''
  if (!addQuestionQuiz.value) return
  try {
    const formData = new FormData()
    // Ensure quiz_id is sent as required by backend
    if (addQuestionQuiz.value && addQuestionQuiz.value.id) {
      formData.append('quiz_id', addQuestionQuiz.value.id)
    }
    if (newQuestion.value.questionType) formData.append('question_type', newQuestion.value.questionType)
    if (newQuestion.value.question_title) formData.append('question_title', newQuestion.value.question_title)
    if (newQuestion.value.questionType === 'image' && newQuestion.value.question_statement_image) {
      formData.append('question_statement_image', newQuestion.value.question_statement_image)
    }
    if (newQuestion.value.question_statement) formData.append('question_statement', newQuestion.value.question_statement)
    if (newQuestion.value.option_1) formData.append('option_1', newQuestion.value.option_1)
    if (newQuestion.value.option_2) formData.append('option_2', newQuestion.value.option_2)
    if (newQuestion.value.option_3) formData.append('option_3', newQuestion.value.option_3)
    if (newQuestion.value.option_4) formData.append('option_4', newQuestion.value.option_4)
    if (newQuestion.value.correct_options) formData.append('correct_options', JSON.stringify(newQuestion.value.correct_options))
    if (newQuestion.value.score) formData.append('score', newQuestion.value.score)
    await axios.post(`http://localhost:5000/api/admin/questions`, formData, { withCredentials: true })
    showAddQuestionForm.value = false
    await fetchQuizzes() // Refresh quizzes section after adding question
  } catch (e) {
    addQuestionError.value = e?.response?.data?.message || 'Failed to add question.'
  }
}
</script>

<style scoped>
/* Stats Table - match score section in UserDashboard.vue */
.stats-table-wrapper {
  width: 100%;
  max-width: 1200px;
  margin: 2.5rem auto 0 auto;
  background: rgba(30, 30, 30, 0.22);
  border-radius: 32px;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  border: 1.5px solid rgba(79,209,197,0.18);
  padding: 2.2rem 2.5rem 2rem 2.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.stats-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 1.2rem;
  margin-top: 1rem;
}
.stats-table th, .stats-table td {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.15rem;
  color: #fff;
  padding: 1.1rem 1.2rem;
  text-align: left;
}
.stats-table th {
  color: #4fd1c5;
  font-weight: 600;
  background: rgba(79,209,197,0.10);
  border: none;
}
.stats-table td {
  background: rgba(30, 30, 30, 0.32);
  border: none;
}
.stats-table tr {
  transition: box-shadow 0.2s, border 0.2s, background 0.2s;
}
.stats-table tr:hover td {
  background: rgba(79,209,197,0.10);
}
/* Add Question Form: options row and tick style for correct options */
.options-row {
  display: flex;
  gap: 1.2rem;
  margin-bottom: 0.7rem;
}
.correct-options-radios {
  display: flex;
  gap: 1.2rem;
  margin-bottom: 0.5rem;
}
.radio-label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-family: 'Orbitron', sans-serif;
  color: #4fd1c5;
  font-size: 1rem;
}
.radio-label input[type="radio"] {
  accent-color: #4fd1c5;
  width: 1.2rem;
  height: 1.2rem;
  border-radius: 6px;
  margin-right: 0.3rem;
}
.dashboard-page-wrapper {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  position: relative;
  background: #000;
}
.vanta-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0;
}
.admin-layout {
  display: flex;
  height: 90vh;
  align-items: center;
  position: relative;
  z-index: 1;
  margin-left: 2.5rem;
  margin-right: 2.5rem;
  margin-top: 2.5rem;
  margin-bottom: 2.5rem;
}
.admin-sidebar {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  min-width: 250px;
  margin-right: 2.5rem;
  height: 100%;
}
.view-as-student-wrapper {
  width: 100%;
  display: flex;
  margin-top: 2.5rem;
  justify-content: center;
}
.view-as-student-btn {
  background: rgba(79,209,197,0.18);
  color: #4fd1c5;
  border: 1.5px solid rgba(79,209,197,0.28);
  border-radius: 18px;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.1rem;
  padding: 0.7rem 2.2rem;
  cursor: pointer;
  box-shadow: 0 2px 8px 0 rgba(79,209,197,0.08);
  transition: background 0.2s, color 0.2s, box-shadow 0.2s;
  margin-bottom: 0.5rem;
}
.view-as-student-btn:hover {
  background: #4fd1c5;
  color: #181c2f;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.18);
}
.admin-navbar-container {
  width: 250px;
  min-width: 220px;
  height: 520px;
  background: rgba(30, 30, 30, 0.22);
  border-radius: 32px;
  box-shadow: 0 0 32px 8px rgba(79,209,197,0.10);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 1.5rem 2rem 1.5rem;
  position: relative;
  z-index: 2;
  margin-top: 4.5rem;
  border: 1.5px solid rgba(79,209,197,0.18);
}
.admin-navbar {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}
.admin-navbar ul {
  list-style: none;
  padding: 0;
  margin: 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 1.1rem;
}
.admin-navbar li {
  display: flex;
  align-items: center;
  gap: 1.1rem;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.18rem;
  color: #fff;
  width: 100%;
  height: 56px;
  padding: 0 1.2rem;
  border-radius: 18px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s, box-shadow 0.2s;
  background: rgba(255,255,255,0.04);
  box-shadow: 0 2px 8px 0 rgba(79,209,197,0.04);
  justify-content: flex-start;
}
.admin-navbar li:last-child {
  margin-bottom: 0;
}
.admin-navbar li.active, .admin-navbar li:hover {
  background: rgba(79,209,197,0.18);
  color: #4fd1c5;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
}
.admin-navbar .icon {
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.main-content-vertical {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  height: 100%;
  justify-content: flex-start;
  margin-right: 0;
  margin-top: 0;
  min-height: 700px;
  min-width: 700px;
  flex: 1;
  background: rgba(30, 30, 30, 0.18);
  color: #fff;
  position: relative;
  z-index: 1;
  border-radius: 32px;
  box-shadow: 0 0 32px 8px rgba(79,209,197,0.10);
  padding-top: 0;
}
.admin-searchbar {
  width: 540px;
  margin-top: 2.5rem;
  margin-bottom: 2.5rem;
  display: flex;
  align-items: center;
  background: rgba(30, 30, 30, 0.22);
  border-radius: 18px;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  backdrop-filter: blur(18px) saturate(180%);
  -webkit-backdrop-filter: blur(18px) saturate(180%);
  border: 1.5px solid rgba(79,209,197,0.18);
  padding: 0.7rem 1.5rem;
  position: relative;
  margin-left: auto;
  margin-right: auto;
}
.search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #fff;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.15rem;
  padding: 0.2rem 0.5rem;
}
.search-input::placeholder {
  color: #4fd1c5bb;
  font-family: 'Orbitron', sans-serif;
}
.search-icon {
  font-size: 1.3rem;
  color: #4fd1c5;
  margin-left: 0.7rem;
  z-index: 2;
  cursor: pointer;
  position: relative;
}
.search-clear {
  cursor: pointer;
  margin-left: 1rem;
  color: #ff1744;
  font-size: 1.7rem;
  z-index: 3;
  position: relative;
}
.dashboard-title {
  font-family: 'Megum', 'Montserrat', sans-serif;
  font-size: 3rem;
  margin-bottom: 0.5rem;
}
.dashboard-sub {
  font-family: 'Orbitron', sans-serif;
  font-size: 1rem;
  color: #4fd1c5;
}
.loading-spinner {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
}
.no-subjects {
  text-align: center;
  color: #4fd1c5;
  font-size: 1.2rem;
  margin-top: 2rem;
}
.subjects-loading {
  text-align: center;
  color: #4fd1c5;
  font-size: 1.2rem;
  margin-top: 2rem;
}
.subjects-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2.5rem;
  margin-top: 2rem;
  width: 100%;
}
.subject-card {
  position: relative;
  background: rgba(30, 30, 30, 0.22);
  border-radius: 24px;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  border: 1.5px solid rgba(79,209,197,0.18);
  padding: 1.5rem 1.2rem 1.2rem 1.2rem;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  width: 600px;
  margin: 0 auto;
}
.card-x-btn {
  position: absolute;
  top: 12px;
  right: 18px;
  background: transparent;
  border: none;
  color: #ff6b6b;
  font-size: 1.7rem;
  font-weight: bold;
  cursor: pointer;
  z-index: 2;
  transition: color 0.2s;
}
.card-x-btn:hover {
  color: #fff;
}
.subject-card-header {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.4rem;
  color: #4fd1c5;
  margin-bottom: 1rem;
  text-align: center;
}
.subject-chapter-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}
.subject-chapter-table th, .subject-chapter-table td {
  border-bottom: 1px solid rgba(79,209,197,0.10);
  padding: 0.5rem 0.7rem;
  text-align: left;
  font-size: 1rem;
}
.subject-chapter-table th {
  color: #4fd1c5;
  font-weight: 600;
  background: rgba(79,209,197,0.06);
}
.chapter-action-btn {
  margin-right: 0.5rem;
  padding: 0.3rem 1.1rem;
  border-radius: 12px;
  border: none;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.98rem;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.chapter-action-btn.edit {
  background: #232b3b;
  color: #4fd1c5;
}
.chapter-action-btn.delete {
  background: #4fd1c5;
  color: #232b3b;
}
.subject-card-footer {
  display: flex;
  justify-content: flex-end;
}
.add-chapter-btn {
  background: rgba(79,209,197,0.18);
  color: #4fd1c5;
  border: 1.5px solid rgba(79,209,197,0.28);
  border-radius: 12px;
  font-family: 'Orbitron', sans-serif;
  font-size: 1rem;
  padding: 0.5rem 1.5rem;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.add-chapter-btn:hover {
  background: #4fd1c5;
  color: #181c2f;
}
.add-subject-btn-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 2.5rem;
}
.add-subject-btn {
  background: #4fd1c5;
  color: #181c2f;
  border: none;
  border-radius: 18px;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.1rem;
  padding: 0.8rem 2.5rem;
  cursor: pointer;
  box-shadow: 0 2px 8px 0 rgba(79,209,197,0.08);
  transition: background 0.2s, color 0.2s, box-shadow 0.2s;
}
.add-subject-btn:hover {
  background: #232b3b;
  color: #4fd1c5;
}
.add-subject-form-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}
.add-subject-form {
  background: rgba(30, 30, 30, 0.22);
  border-radius: 24px;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  border: 1.5px solid rgba(79,209,197,0.18);
  padding: 2.2rem 3.5rem 2rem 3.5rem;
  display: flex;
  flex-direction: column;
  min-width: 420px;
  max-width: 600px;
  width: 100%;
}
.add-chapter-form-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}
.add-chapter-form {
  background: rgba(30, 30, 30, 0.22);
  border-radius: 24px;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  border: 1.5px solid rgba(79,209,197,0.18);
  padding: 2.2rem 3.5rem 2rem 3.5rem;
  display: flex;
  flex-direction: column;
  min-width: 420px;
  max-width: 600px;
  width: 100%;
}
.add-quiz-form {
  background: rgba(30, 30, 30, 0.22);
  border-radius: 24px;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  border: 1.5px solid rgba(79,209,197,0.18);
  padding: 2.2rem 3.5rem 2rem 3.5rem;
  display: flex;
  flex-direction: column;
  min-width: 420px;
  max-width: 600px;
  width: 100%;
}
@media (min-width: 700px) {
 
  .add-quiz-form {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 2rem;
    max-width: 900px;
  }
  .add-quiz-form .form-group {
    flex: 1 1 40%;
    min-width: 280px;
    margin-bottom: 1.1rem;
  }
  .add-quiz-form .form-actions {
    flex-basis: 100%;
    justify-content: flex-end;
    margin-top: 2rem;
  }
}
.add-quiz-form .form-title {
  flex-basis: 100%;
  text-align: center;
  margin-bottom: 1 rem;
}
.form-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.3rem;
  color: #4fd1c5;
  margin-bottom: 1 rem;
  text-align: center;
}
.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
}
.form-group label {
  color: #4fd1c5;
  font-size: 1rem;
  margin-bottom: 0.3rem;
  font-family: 'Orbitron', sans-serif;
}
.form-group input,
.form-group textarea {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(79,209,197,0.18);
  border-radius: 10px;
  color: #fff;
  font-size: 1rem;
  font-family: 'Orbitron', sans-serif;
  padding: 0.5rem 0.8rem;
  outline: none;
  transition: border 0.2s;
}
.form-group input:focus,
.form-group textarea:focus {
  border: 1.5px solid #4fd1c5;
}
.form-group textarea {
  min-height: 60px;
  resize: vertical;
}
.form-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 1.2rem;
}
.form-btn {
  background: rgba(79,209,197,0.18);
  color: #4fd1c5;
  border: 1.5px solid rgba(79,209,197,0.28);
  border-radius: 12px;
  font-family: 'Orbitron', sans-serif;
  font-size: 1rem;
  padding: 0.5rem 1.5rem;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.form-btn.submit {
  background: #4fd1c5;
  color: #181c2f;
}
.form-btn.submit:hover {
  background: #232b3b;
  color: #4fd1c5;
}
.form-btn.back:hover {
  background: #232b3b;
  color: #4fd1c5;
}
.form-error {
  color: #ff6b6b;
  font-size: 1rem;
  margin-bottom: 0.7rem;
  text-align: center;
}
.content-section > h1.dashboard-title,
.content-section > p.dashboard-sub {
  text-align: center;
  margin-left: auto;
  margin-right: auto;
}
.delete-subject-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: rgba(30, 30, 30, 0.95);
  border-radius: 18px;
  box-shadow: 0 0 32px 8px rgba(79,209,197,0.18);
  padding: 2.2rem 2.5rem 2rem 2.5rem;
  min-width: 340px;
  max-width: 40vw;
  color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  color: #fff;
  font-size: 1.5rem;
  cursor: pointer;
}
.modal-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.3rem;
  color: #ff6b6b;
  margin-bottom: 1.2rem;
}
.modal-body {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  text-align: center;
}
.modal-actions {
  display: flex;
  gap: 1.2rem;
}
.modal-btn {
  background: rgba(79,209,197,0.18);
  color: #4fd1c5;
  border: 1.5px solid rgba(79,209,197,0.28);
  border-radius: 12px;
  font-family: 'Orbitron', sans-serif;
  font-size: 1rem;
  padding: 0.5rem 1.5rem;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.modal-btn.delete {
  background: #ff6b6b;
  color: #fff;
}
.modal-btn.delete:hover {
  background: #232b3b;
  color: #ff6b6b;
}
.modal-btn.cancel:hover {
  background: #232b3b;
  color: #4fd1c5;
}
.edit-chapter-form-outer-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.add-quiz-btn {
  background: #4fd1c5;
  color: #181c2f;
  border: none;
  border-radius: 18px;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.1rem;
  padding: 0.8rem 2.5rem;
  cursor: pointer;
  box-shadow: 0 2px 8px 0 rgba(79,209,197,0.08);
  transition: background 0.2s, color 0.2s, box-shadow 0.2s;
  margin-top: 2rem;
}
.add-quiz-btn:hover {
  background: #232b3b;
  color: #4fd1c5;
}
.add-quiz-form-outer-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}
.add-quiz-form {
  background: rgba(30, 30, 30, 0.22);
  border-radius: 24px;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  border: 1.5px solid rgba(79,209,197,0.18);
  padding: 2.2rem 3.5rem 2rem 3.5rem;
  display: flex;
  flex-direction: column;
  min-width: 420px;
  max-width: 600px;
  width: 100%;
}
@media (min-width: 700px) {
  .add-quiz-form {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 2rem;
    max-width: 900px;
  }
  .add-quiz-form .form-group {
    flex: 1 1 40%;
    min-width: 280px;
    margin-bottom: 1.1rem;
  }
  .add-quiz-form .form-actions {
    flex-basis: 100%;
    justify-content: flex-end;
    margin-top: 2rem;
  }
}
.add-quiz-form .form-title {
  flex-basis: 100%;
  text-align: center;
  margin-bottom: 1 rem;
}
.styled-select {
  background: #4fd1c5;
  border: 1px solid rgba(79,209,197,0.28);
  border-radius: 10px;
  color: #181c2f;
  font-size: 1rem;
  font-family: 'Orbitron', sans-serif;
  padding: 0.5rem 0.8rem;
  outline: none;
  transition: border 0.2s;
  width: 100%;
}
.styled-select:focus {
  border: 1.5px solid #232b3b;
}
.form-group-marks-actions {
  position: relative;
}
.form-actions-inline {
  display: flex;
  gap: 1.2rem;
  margin-top: 0.7rem;
}

.add-question-form-outer-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.add-question-form {
  background: rgba(30, 30, 30, 0.22);
  border-radius: 24px;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  border: 1.5px solid rgba(79,209,197,0.18);
  padding: 2.2rem 3.5rem 2rem 3.5rem;
  display: flex;
  flex-direction: column;
  min-width: 1220px;
}
@media (min-width: 700px) {
  .add-question-form {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 2rem;
    max-width: 900px;
  }
  .add-question-form .form-group {
    flex: 1 1 40%;
    min-width: 280px;
    margin-bottom: 1.1rem;
  }
  .add-question-form .form-actions {
    flex-basis: 100%;
    justify-content: flex-end;
    margin-top: 2rem;
  }
}
.add-question-form .form-title {
  flex-basis: 100%;
  text-align: center;
  margin-bottom: 1rem;
}
.add-question-form .form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
}
.add-question-form .form-group label {
  color: #4fd1c5;
  font-size: 1rem;
  margin-bottom: 0.3rem;
  font-family: 'Orbitron', sans-serif;
}
.add-question-form .form-group input,
.add-question-form .form-group textarea,
.add-question-form .form-group select {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(79,209,197,0.18);
  border-radius: 10px;
  color: #fff;
  font-size: 1rem;
  font-family: 'Orbitron', sans-serif;
  padding: 0.5rem 0.8rem;
  outline: none;
  transition: border 0.2s;
}
.add-question-form .form-group input:focus,
.add-question-form .form-group textarea:focus,
.add-question-form .form-group select:focus {
  border: 1.5px solid #4fd1c5;
}
.add-question-form .form-group textarea {
  min-height: 60px;
  resize: vertical;
}
.add-question-form .form-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 1.2rem;
}
.add-question-form .form-btn {
  background: rgba(79,209,197,0.18);
  color: #4fd1c5;
  border: 1.5px solid rgba(79,209,197,0.28);
  border-radius: 12px;
  font-family: 'Orbitron', sans-serif;
  font-size: 1rem;
  padding: 0.5rem 1.5rem;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.add-question-form .form-btn.submit {
  background: #4fd1c5;
  color: #181c2f;
}
.add-question-form .form-btn.submit:hover {
  background: #232b3b;
  color: #4fd1c5;
}
.add-question-form .form-btn.back:hover {
  background: #232b3b;
  color: #4fd1c5;
}
.add-question-form .form-error {
  color: #ff6b6b;
  font-size: 1rem;
  margin-bottom: 0.7rem;
  text-align: center;
}
</style>
