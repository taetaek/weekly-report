/**
 * 주간 일정 리포트 - 실시간 API
 * Google Apps Script 웹 앱으로 배포. 대시보드 페이지가 새로고침될 때마다
 * 이 엔드포인트를 호출해 그 순간의 캘린더 상태를 그대로 반환한다.
 *
 * 배포: 배포 > 새 배포 > 웹 앱
 *   - 실행 방식: 나 (Me)
 *   - 액세스 권한: 모든 사용자 (Anyone)
 * 비밀번호는 코드에 하드코딩하지 않고 프로젝트 설정 > 스크립트 속성(ACCESS_PASSWORD)에 저장한다.
 */

var CALENDAR_IDS = {
  "자기계발_취미": "phr0n4324p0g5d1jn8hp5e9cac@group.calendar.google.com",
  "개인업무": "pofffq28pj9hidjjdbnendj8bk@group.calendar.google.com",
  "자유시간": "lq8b26n6a4gunllrr2em6a0aq4@group.calendar.google.com",
  "문화생활": "gnq6n2tfa0eu6qg3p60hn8am5k@group.calendar.google.com"
};

var ACTIVITY_KEYWORDS = {
  "영어": ["영어", "잉글리시버디"],
  "경제": ["부동산", "경매", "경제공부"],
  "운동": ["운동", "농구", "클라이밍", "코트메이트", "두스켓볼"],
  "창작&학습": ["WWT", "Gathering", "클로더스", "스터디", "책생각", "독서", "서포테스트"],
  "음악": ["드럼", "캐롤라인"]
};

var CATEGORY_EMOJI = {
  "영어": "🗣",
  "경제": "💰",
  "운동": "🏃",
  "창작&학습": "📚",
  "음악": "🎵",
  "휴식": "🛋"
};

var REST_CALENDAR = "자유시간";
var GRAPHITE_COLOR_ID = "8";
var ALL_WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"];
var TIMEZONE = "Asia/Seoul";

function doGet(e) {
  var password = e.parameter.password || "";
  var expected = PropertiesService.getScriptProperties().getProperty("ACCESS_PASSWORD");

  if (!expected || password !== expected) {
    return jsonOutput({ error: "unauthorized" });
  }

  try {
    var thisWeek = getWeekRange(0);
    var lastWeek = getWeekRange(1);

    var thisWeekEvents = fetchAllEvents(thisWeek.start, thisWeek.end);
    var lastWeekEvents = fetchAllEvents(lastWeek.start, lastWeek.end);

    var result = analyze(thisWeekEvents);
    var lastResult = analyze(lastWeekEvents);
    result.graphiteCount = lastResult.graphiteCount;
    result.graphiteCategories = lastResult.graphiteCategories;
    result.graphiteEvents = lastResult.graphiteEvents;

    var payload = {
      weekStart: formatDate(thisWeek.monday),
      weekEnd: formatDate(thisWeek.sunday),
      categories: Object.keys(CATEGORY_EMOJI).map(function (cat) {
        return {
          name: cat,
          emoji: CATEGORY_EMOJI[cat],
          count: result.activityCounts[cat] || 0,
          details: result.activityDetails[cat] || []
        };
      }),
      emptyDays: ALL_WEEKDAYS.filter(function (d) {
        return result.activeDays.indexOf(d) === -1;
      }),
      graphiteCount: result.graphiteCount,
      graphiteCategories: result.graphiteCategories,
      graphiteEvents: result.graphiteEvents,
      generatedAt: new Date().toISOString()
    };

    return jsonOutput(payload);
  } catch (err) {
    return jsonOutput({ error: String(err) });
  }
}

function jsonOutput(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function formatDate(date) {
  return Utilities.formatDate(date, TIMEZONE, "yyyy.MM.dd");
}

function getWeekRange(offsetWeeks) {
  var now = new Date(Utilities.formatDate(new Date(), TIMEZONE, "yyyy-MM-dd'T'HH:mm:ss"));
  var weekday = (now.getDay() + 6) % 7; // 월=0 ... 일=6
  var monday = new Date(now);
  monday.setDate(now.getDate() - weekday - offsetWeeks * 7);
  monday.setHours(0, 0, 0, 0);

  var sunday = new Date(monday);
  sunday.setDate(monday.getDate() + 6);
  sunday.setHours(23, 59, 59, 999);

  var start = new Date(monday);
  var end = new Date(sunday);
  end.setDate(end.getDate() + 1); // CalendarApp.getEvents end는 배타적이므로 하루 더

  return { start: start, end: end, monday: monday, sunday: sunday };
}

function fetchAllEvents(start, end) {
  var allEvents = {};
  Object.keys(CALENDAR_IDS).forEach(function (name) {
    var calId = CALENDAR_IDS[name];
    try {
      var cal = CalendarApp.getCalendarById(calId);
      var events = cal ? cal.getEvents(start, end) : [];
      allEvents[name] = events;
    } catch (err) {
      allEvents[name] = [];
    }
  });
  return allEvents;
}

function getWeekdayName(date) {
  var idx = (date.getDay() + 6) % 7;
  return ALL_WEEKDAYS[idx];
}

function classifyActivity(summary) {
  var lower = summary.toLowerCase();
  var matched = [];
  Object.keys(ACTIVITY_KEYWORDS).forEach(function (category) {
    var keywords = ACTIVITY_KEYWORDS[category];
    for (var i = 0; i < keywords.length; i++) {
      if (lower.indexOf(keywords[i].toLowerCase()) !== -1) {
        matched.push(category);
        break;
      }
    }
  });
  return matched;
}

function analyze(allEventsByCalendar) {
  var activityCounts = {};
  var activityDetails = {};
  Object.keys(ACTIVITY_KEYWORDS).forEach(function (cat) {
    activityCounts[cat] = 0;
    activityDetails[cat] = [];
  });
  activityCounts["휴식"] = 0;
  activityDetails["휴식"] = [];

  var graphiteCount = 0;
  var graphiteEvents = [];
  var graphiteCategoriesSet = {};
  var activeDaysSet = {};

  Object.keys(allEventsByCalendar).forEach(function (calName) {
    var events = allEventsByCalendar[calName];
    events.forEach(function (event) {
      var summary = event.getTitle() || "";
      var colorId = event.getColor() || "";
      var eventDate = event.isAllDayEvent() ? event.getAllDayStartDate() : event.getStartTime();
      if (!eventDate) return;
      var weekday = getWeekdayName(eventDate);

      if (colorId === GRAPHITE_COLOR_ID) {
        graphiteCount++;
        graphiteEvents.push(summary);
        if (summary.indexOf("일정") === -1) {
          classifyActivity(summary).forEach(function (cat) {
            graphiteCategoriesSet[cat] = true;
          });
        }
      }

      if (calName === REST_CALENDAR) {
        activityCounts["휴식"]++;
        activityDetails["휴식"].push(summary);
        activeDaysSet[weekday] = true;
        return;
      }

      if (summary.indexOf("일정") !== -1) return;
      var matchedCategories = classifyActivity(summary);
      matchedCategories.forEach(function (cat) {
        activityCounts[cat]++;
        activityDetails[cat].push(summary);
      });
      if (matchedCategories.length > 0) activeDaysSet[weekday] = true;
    });
  });

  return {
    activityCounts: activityCounts,
    activityDetails: activityDetails,
    graphiteCount: graphiteCount,
    graphiteEvents: graphiteEvents,
    graphiteCategories: Object.keys(graphiteCategoriesSet).sort(),
    activeDays: Object.keys(activeDaysSet)
  };
}
