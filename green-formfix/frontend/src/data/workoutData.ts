//src/data/workoutData.ts
export interface Exercise {
  id: string;
  name: string;
  sets: number;
  reps: string;
  muscle: string;
  description: string;
  tips: string[];
}

export interface WorkoutDay {
  id: string;
  name: string;
  focus: string;
  exercises: Exercise[];
}

export interface WorkoutPlan {
  id: string;
  name: string;
  description: string;
  image: string;
  days: WorkoutDay[];
}

export const pushPullLegPlan: WorkoutPlan = {
  id: "ppl",
  name: "Push Pull Legs",
  description: "A high-efficiency split targeting functional movement patterns for total body power and symmetry.",
  image: "push",
  days: [
    {
      id: "push",
      name: "Push Day",
      focus: "Chest, Shoulders, Triceps",
      exercises: [
        { id: "bp", name: "Barbell Bench Press", sets: 4, reps: "8-10", muscle: "Chest", description: "Lie on bench, lower bar to chest, press up.", tips: ["Keep feet flat", "Arch slightly", "Squeeze chest at top"] },
        { id: "ohp", name: "Overhead Press", sets: 4, reps: "8-10", muscle: "Shoulders", description: "Press barbell overhead from shoulder level.", tips: ["Brace core", "Don't lean back", "Full lockout"] },
        { id: "idf", name: "Incline Dumbbell Fly", sets: 3, reps: "12-15", muscle: "Upper Chest", description: "Open arms wide on incline bench, squeeze together.", tips: ["Slight bend in elbows", "Control the negative", "Feel the stretch"] },
        { id: "lr", name: "Lateral Raises", sets: 4, reps: "12-15", muscle: "Side Delts", description: "Raise dumbbells to sides until arms parallel.", tips: ["Lead with elbows", "Don't swing", "Slow negative"] },
        { id: "tpd", name: "Tricep Pushdowns", sets: 3, reps: "12-15", muscle: "Triceps", description: "Push cable down, squeezing triceps.", tips: ["Keep elbows pinned", "Full extension", "Squeeze at bottom"] },
        { id: "dips", name: "Dips", sets: 3, reps: "10-12", muscle: "Chest/Triceps", description: "Lower body between parallel bars, push up.", tips: ["Lean forward for chest", "Stay upright for triceps", "Full range"] },
      ],
    },
    {
      id: "pull",
      name: "Pull Day",
      focus: "Back, Biceps, Rear Delts",
      exercises: [
        { id: "dl", name: "Deadlift", sets: 4, reps: "5-6", muscle: "Back", description: "Lift barbell from floor to standing.", tips: ["Hinge at hips", "Keep bar close", "Neutral spine"] },
        { id: "br", name: "Barbell Rows", sets: 4, reps: "8-10", muscle: "Back", description: "Bend over, row barbell to lower chest.", tips: ["45-degree angle", "Squeeze shoulder blades", "Control the weight"] },
        { id: "pu", name: "Pull-Ups", sets: 4, reps: "8-12", muscle: "Lats", description: "Hang from bar, pull chin over.", tips: ["Full dead hang", "Lead with chest", "Controlled descent"] },
        { id: "fc", name: "Face Pulls", sets: 3, reps: "15-20", muscle: "Rear Delts", description: "Pull rope to face, externally rotate.", tips: ["High cable", "Pause at contraction", "Light weight"] },
        { id: "bc", name: "Barbell Curls", sets: 3, reps: "10-12", muscle: "Biceps", description: "Curl barbell with strict form.", tips: ["No swinging", "Squeeze at top", "Slow negative"] },
        { id: "hc", name: "Hammer Curls", sets: 3, reps: "12-15", muscle: "Brachialis", description: "Curl dumbbells with neutral grip.", tips: ["Palms face in", "Alternate arms", "Full range"] },
      ],
    },
    {
      id: "legs",
      name: "Leg Day",
      focus: "Quads, Hamstrings, Glutes, Calves",
      exercises: [
        { id: "sq", name: "Barbell Squats", sets: 4, reps: "6-8", muscle: "Quads", description: "Squat with barbell on upper back.", tips: ["Break at hips first", "Knees track toes", "Hit parallel"] },
        { id: "rdl", name: "Romanian Deadlift", sets: 4, reps: "8-10", muscle: "Hamstrings", description: "Hinge at hips with slight knee bend.", tips: ["Push hips back", "Feel hamstring stretch", "Keep bar close"] },
        { id: "lp", name: "Leg Press", sets: 3, reps: "10-12", muscle: "Quads", description: "Press platform away on leg press machine.", tips: ["Full range", "Don't lock knees", "Feet shoulder width"] },
        { id: "lc", name: "Leg Curls", sets: 3, reps: "12-15", muscle: "Hamstrings", description: "Curl weight using hamstrings on machine.", tips: ["Control the negative", "Full contraction", "Don't use momentum"] },
        { id: "bu", name: "Bulgarian Split Squats", sets: 3, reps: "10-12", muscle: "Quads/Glutes", description: "Rear foot elevated single leg squat.", tips: ["Stay upright", "Push through front heel", "Control balance"] },
        { id: "cr", name: "Calf Raises", sets: 4, reps: "15-20", muscle: "Calves", description: "Rise onto toes, squeeze calves.", tips: ["Full stretch at bottom", "Pause at top", "Slow tempo"] },
      ],
    },
  ],
};

export const highVolumeSplitPlan: WorkoutPlan = {
  id: "volume-split",
  name: "Body Part Split",
  description: "A precision 5-day split designed for maximum muscle focus and high-volume hypertrophy.",
  image: "split",
  days: [
    {
      id: "chest",
      name: "Chest Focus",
      focus: "Chest",
      exercises: [
        { id: "bbp", name: "Flat Bench Press", sets: 4, reps: "6-8", muscle: "Chest", description: "Classic barbell bench press.", tips: ["Retract scapula", "Drive feet", "Control descent"] },
        { id: "ibp", name: "Incline Bench Press", sets: 4, reps: "8-10", muscle: "Upper Chest", description: "Press on 30-45 degree incline.", tips: ["30-45 degrees", "Touch upper chest", "Full lockout"] },
        { id: "cf", name: "Cable Flyes", sets: 3, reps: "12-15", muscle: "Chest", description: "Cross cables in front of chest.", tips: ["Squeeze together", "Constant tension", "Slight forward lean"] },
        { id: "dfly", name: "Dumbbell Flyes", sets: 3, reps: "12-15", muscle: "Chest", description: "Open arms wide, bring dumbbells together.", tips: ["Slight elbow bend", "Feel the stretch", "Don't go too heavy"] },
      ],
    },
    {
      id: "back",
      name: "Back Focus",
      focus: "Back",
      exercises: [
        { id: "bdl", name: "Barbell Rows", sets: 4, reps: "6-8", muscle: "Back", description: "Bent over barbell row.", tips: ["45 degree torso", "Pull to navel", "Squeeze blades"] },
        { id: "lpd", name: "Lat Pulldowns", sets: 4, reps: "10-12", muscle: "Lats", description: "Pull bar to upper chest.", tips: ["Lean slightly back", "Pull with elbows", "Full stretch"] },
        { id: "sr", name: "Seated Cable Row", sets: 3, reps: "10-12", muscle: "Mid Back", description: "Row cable handle to torso.", tips: ["Chest up", "Pause at contraction", "Full extension"] },
        { id: "bpu", name: "Pull-Ups", sets: 3, reps: "Max", muscle: "Lats", description: "Wide grip pull-ups.", tips: ["Full range", "No kipping", "Add weight if easy"] },
      ],
    },
    {
      id: "shoulders",
      name: "Shoulder Focus",
      focus: "Shoulders",
      exercises: [
        { id: "mp", name: "Military Press", sets: 4, reps: "6-8", muscle: "Front Delts", description: "Strict overhead barbell press.", tips: ["Brace core", "Full lockout", "Controlled descent"] },
        { id: "slr", name: "Lateral Raises", sets: 4, reps: "12-15", muscle: "Side Delts", description: "Raise dumbbells to sides.", tips: ["Lead with elbows", "Slight forward lean", "Pause at top"] },
        { id: "rfp", name: "Reverse Flyes", sets: 3, reps: "15-20", muscle: "Rear Delts", description: "Bend over, raise dumbbells out.", tips: ["Pinch shoulder blades", "Light weight", "High reps"] },
        { id: "shr", name: "Shrugs", sets: 3, reps: "12-15", muscle: "Traps", description: "Shrug shoulders up with heavy weight.", tips: ["Hold at top", "Don't roll", "Heavy weight"] },
      ],
    },
    {
      id: "arms",
      name: "Arm Focus",
      focus: "Biceps & Triceps",
      exercises: [
        { id: "abc", name: "Barbell Curls", sets: 4, reps: "8-10", muscle: "Biceps", description: "Strict barbell curls.", tips: ["No swinging", "Full range", "Squeeze top"] },
        { id: "skc", name: "Skull Crushers", sets: 4, reps: "8-10", muscle: "Triceps", description: "Lower bar to forehead, extend.", tips: ["Elbows in", "Control weight", "Full extension"] },
        { id: "pc", name: "Preacher Curls", sets: 3, reps: "10-12", muscle: "Biceps", description: "Curl on preacher bench.", tips: ["Full stretch", "Don't swing", "Squeeze peak"] },
        { id: "otx", name: "Overhead Tricep Extension", sets: 3, reps: "10-12", muscle: "Triceps", description: "Extend dumbbell overhead.", tips: ["Keep elbows close", "Full stretch", "Squeeze lockout"] },
      ],
    },
    {
      id: "blegs",
      name: "Lower Body",
      focus: "Legs",
      exercises: [
        { id: "bsq", name: "Squats", sets: 4, reps: "6-8", muscle: "Quads", description: "Barbell back squats.", tips: ["Full depth", "Brace core", "Drive through heels"] },
        { id: "brdl", name: "Romanian Deadlift", sets: 4, reps: "8-10", muscle: "Hamstrings", description: "Hip hinge with barbell.", tips: ["Push hips back", "Slight knee bend", "Feel stretch"] },
        { id: "ble", name: "Leg Extensions", sets: 3, reps: "12-15", muscle: "Quads", description: "Extend legs on machine.", tips: ["Pause at top", "Control negative", "Full extension"] },
        { id: "blc", name: "Leg Curls", sets: 3, reps: "12-15", muscle: "Hamstrings", description: "Curl on machine.", tips: ["Full range", "Slow negative", "Squeeze top"] },
      ],
    },
  ],
};

export const sampleRecipes = [
  {
    id: "1",
    title: "High Protein Chicken Bowl",
    description: "Grilled chicken breast with quinoa, avocado, and mixed greens. Perfect post-workout meal.",
    calories: 520,
    protein: 45,
    carbs: 42,
    fat: 18,
  },
  {
    id: "2",
    title: "Protein Smoothie Bowl",
    description: "Banana, whey protein, oats, peanut butter, and berries blended thick.",
    calories: 480,
    protein: 38,
    carbs: 55,
    fat: 14,
  },
  {
    id: "3",
    title: "Salmon & Sweet Potato",
    description: "Baked salmon fillet with roasted sweet potato and steamed broccoli.",
    calories: 580,
    protein: 42,
    carbs: 38,
    fat: 24,
  },
  {
    id: "4",
    title: "Greek Yogurt Parfait",
    description: "Greek yogurt layered with granola, honey, and fresh berries.",
    calories: 350,
    protein: 28,
    carbs: 40,
    fat: 8,
  },
  {
    id: "5",
    title: "Steak & Rice Bowl",
    description: "Lean sirloin steak with jasmine rice, peppers, and teriyaki sauce.",
    calories: 620,
    protein: 48,
    carbs: 52,
    fat: 20,
  },
  {
    id: "6",
    title: "Egg White Omelette",
    description: "Egg whites with spinach, mushrooms, tomatoes, and feta cheese.",
    calories: 280,
    protein: 32,
    carbs: 8,
    fat: 12,
  },
];

// Add this at the end of the file to prevent the "export not found" error
export const broSplitPlan = highVolumeSplitPlan;