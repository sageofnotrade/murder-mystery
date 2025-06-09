<template>
  <div class="min-h-screen px-4 sm:px-6 md:px-10 py-16 text-gray-300">
    <!-- INTRO -->
    <section class="text-center mb-16">
      <h1 class="text-4xl sm:text-5xl font-bold text-mystery-accent mb-4">What is Murbrą?</h1>
      <p class="text-base sm:text-lg md:text-xl max-w-3xl mx-auto">
        Murbrą is an adaptive psychological murder mystery powered by artificial intelligence.
        Your decisions shape the world, the suspects—and the truth itself.
      </p>
    </section>

    <!-- FEATURES -->
    <section class="grid sm:grid-cols-2 gap-6 text-left mb-20">
      <div class="bg-mystery-darker p-5 sm:p-6 rounded-xl shadow-lg transition hover:scale-105 hover:shadow-xl">
        <h2 class="text-xl sm:text-2xl font-semibold text-mystery-accent mb-3">🧠 Personalized Mysteries</h2>
        <p>Your gameplay decisions form a psychological profile that influences suspects, clues, and storylines.</p>
      </div>
      <div class="bg-mystery-darker p-5 sm:p-6 rounded-xl shadow-lg transition hover:scale-105 hover:shadow-xl">
        <h2 class="text-xl sm:text-2xl font-semibold text-mystery-accent mb-3">🕵️ Dynamic Characters</h2>
        <p>Suspects evolve with each choice you make—confrontation, empathy, logic—they remember it all.</p>
      </div>
      <div class="bg-mystery-darker p-5 sm:p-6 rounded-xl shadow-lg transition hover:scale-105 hover:shadow-xl">
        <h2 class="text-xl sm:text-2xl font-semibold text-mystery-accent mb-3">🧩 Detective Board</h2>
        <p>Drag and link clues, suspects, and scenes to uncover deeper truths using our interactive visual board.</p>
      </div>
      <div class="bg-mystery-darker p-5 sm:p-6 rounded-xl shadow-lg transition hover:scale-105 hover:shadow-xl">
        <h2 class="text-xl sm:text-2xl font-semibold text-mystery-accent mb-3">💡 Powered by AI</h2>
        <p>Conversations, plot twists, and evidence are dynamically generated through AI, making no two cases the same.</p>
      </div>
    </section>

    <!-- UNIQUE ELEMENTS -->
    <section class="mb-20">
      <h2 class="text-2xl sm:text-3xl font-bold text-mystery-accent mb-6">✨ What Makes Murbrą Different?</h2>
      <ul class="space-y-4 list-disc pl-5 sm:pl-6">
        <li><strong>Memory-based suspects:</strong> NPCs remember your actions and adapt their behavior.</li>
        <li><strong>Emotion-aware branching:</strong> Dialogue trees shift based on tone and approach.</li>
        <li><strong>Evolving psychological profile:</strong> The system profiles you across multiple cases.</li>
      </ul>
    </section>

    <!-- TECH BEHIND THE SCENES -->
    <section class="mb-20">
      <h2 class="text-2xl sm:text-3xl font-bold text-mystery-accent mb-6">🔧 Behind the Scenes</h2>
      <div class="grid gap-6 sm:grid-cols-3">
        <div class="bg-mystery-darker p-4 rounded-lg shadow">
          <h3 class="text-lg font-semibold text-mystery-accent mb-2">🧠 Personality Engine</h3>
          <p class="text-sm">Maps your choices to real psychological traits and affects future case design.</p>
        </div>
        <div class="bg-mystery-darker p-4 rounded-lg shadow">
          <h3 class="text-lg font-semibold text-mystery-accent mb-2">🤖 AI Dialogue</h3>
          <p class="text-sm">Real-time suspect interactions powered by large language models.</p>
        </div>
        <div class="bg-mystery-darker p-4 rounded-lg shadow">
          <h3 class="text-lg font-semibold text-mystery-accent mb-2">📍 Visual Logic</h3>
          <p class="text-sm">Interactive board syncs relationships between all story elements.</p>
        </div>
      </div>
    </section>

    <!-- PLAYER JOURNEY -->
    <section class="mb-20">
      <h2 class="text-2xl sm:text-3xl font-bold text-mystery-accent mb-6">🚶 Your Journey as a Detective</h2>
      <p class="mb-4">You begin as an unknown rookie investigator. The first case is quiet—too quiet. But when a suspect starts referencing a decision you made 15 minutes ago, the reality shifts.</p>
      <p>From there, every case deepens your profile. Suspects will notice patterns. Clues will evolve. And one day, you’ll realize Murbrą has been profiling you, too.</p>
    </section>

    <!-- TESTIMONIALS -->
    <section class="mb-20">
      <h2 class="text-2xl sm:text-3xl font-bold text-mystery-accent mb-6">💬 What Players Say</h2>
      <div class="grid sm:grid-cols-3 gap-6 text-sm">
        <blockquote class="bg-mystery-darker p-4 rounded-lg shadow">
          “I've never replayed a mystery game before—Murbrą made me do it three times.”
        </blockquote>
        <blockquote class="bg-mystery-darker p-4 rounded-lg shadow">
          “A suspect called out my lie based on how I handled a previous case. Freaky. Genius.”
        </blockquote>
        <blockquote class="bg-mystery-darker p-4 rounded-lg shadow">
          “It felt like the game *knew* me. And it used that against me. I loved it.”
        </blockquote>
      </div>
    </section>

    <!-- HELP SECTION -->
    <section id="help" class="bg-mystery-darker/70 p-6 sm:p-8 rounded-xl shadow-lg mb-20">
      <div class="flex items-center mb-4">
        <span class="bg-pink-600 text-white px-3 py-1 rounded-full text-sm mr-3">SOS</span>
        <h2 class="text-xl sm:text-2xl font-bold text-mystery-accent">Help & Support</h2>
      </div>
      <ul class="space-y-2 list-disc pl-5 sm:pl-6">
        <li><strong>Start a Mystery:</strong> Click “Start Your Mystery” on the homepage and register an account.</li>
        <li><strong>Detective Board:</strong> Drag clues, suspects, and locations to connect them visually.</li>
        <li><strong>Progress Tracking:</strong> Your profile logs case history and psychological patterns.</li>
        <li><strong>Need help?</strong> Email us at <a href="mailto:support@murbra.com" class="text-pink-400 underline">support@murbra.com</a>.</li>
      </ul>
    </section>

    <!-- CALL TO ACTION -->
    <div class="text-center">
      <NuxtLink
        to="/auth/register"
        class="inline-block px-6 py-3 rounded-lg text-base sm:text-lg font-semibold bg-mystery-accent text-mystery-dark hover:bg-mystery-accent/90 transition mb-4"
      >
        Start Your Mystery
      </NuxtLink>
      <div>
        <NuxtLink
          to="/"
          class="text-mystery-accent underline hover:text-mystery-accent/80 transition text-sm sm:text-base"
        >
          ← Back to Home
        </NuxtLink>
      </div>
    </div>
  </div>
</template>
