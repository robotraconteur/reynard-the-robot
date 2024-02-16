const socket = io();


let reynard_kinematics = {
    body_offset: new paper.Point(0, 70),
    bounds: new paper.Rectangle(0, 0, 2000, 1000),
    p0: new paper.Point(0, -95),
    p1: new paper.Point(170, 0),
    p1_c: new paper.Point(85, 0),
    p2: new paper.Point(170, 0),
    p2_c: new paper.Point(85, 0),
    p3: new paper.Point(60, 0),
    p3_c: new paper.Point(35, 0),
    q1_bounds: [-10, 180],
    q2_bounds: [-140, 140],
    q3_bounds: [-175, 175]
}


class ReynardRobot {
  constructor() {
    this.canvas = $('#reynard-canvas');
    this.reynard_output = $('#reynard-output');
    this.reynard_talk_input = $('#reynard-talk-input');
    this.reynard_send_submit = $('#reynard-send-submit');
    this.reynard_send_submit.click(this.send.bind(this));
    this.canvas = $('#reynard-canvas').get(0);
    paper.setup(this.canvas);
    paper.view.zoom=0.4;

  }
  send() {
    let send_text = this.reynard_talk_input.val();
    socket.emit('new_message', send_text);
    this.reynard_talk_input.val('');
  }
  async loadReynard() {
    let reynard_group = new paper.Group();
    let reynard_body = await loadSVGImage(reynard_group,'reynard_body.svg');
    let reynard_link1 = await loadSVGImage(reynard_group,'reynard_arm_link.svg');
    let reynard_tool = await loadSVGImage(reynard_group,'reynard_tool.svg');
    let reynard_link2 = await loadSVGImage(reynard_group,'reynard_arm_link.svg');

    setLinkPosition(reynard_body, reynard_link1, reynard_kinematics.p0, reynard_kinematics.p1_c, -5);
    setLinkPosition(reynard_link1, reynard_link2, reynard_kinematics.p1_c, reynard_kinematics.p2_c, -10);
    setLinkPosition(reynard_link2, reynard_tool, reynard_kinematics.p2_c, reynard_kinematics.p3_c, 15);

    setBodyPosition(reynard_group, reynard_body, paper.view.center.subtract(reynard_kinematics.body_offset));

    this.reynard_group = reynard_group;
    this.reynard_body = reynard_body;
    this.reynard_link1 = reynard_link1;
    this.reynard_tool = reynard_tool;
    this.reynard_link2 = reynard_link2;

    socket.on('teleport', (data) => {
      this.teleport(data.x, data.y);
    });

    socket.on('arm', (data) => {
      this.arm(data.q1, data.q2, data.q3);
    });

    socket.on('update', (data) => {
      this.teleport(data.x, data.y);
      this.arm(data.q1, data.q2, data.q3);
    });

    socket.on('say', (text) => {
      this.reynard_output.append(`<div class="output-line">${text}</div>`);
    });

    socket.on('color', (color) => {
      this.changeColor(color.r, color.g, color.b);
    });
  }

  teleport(x, y) {
    if (x > (reynard_kinematics.bounds.x + reynard_kinematics.bounds.width/2)) {
      x = reynard_kinematics.bounds.x + reynard_kinematics.bounds.width/2;
    }
    if (x < reynard_kinematics.bounds.x - reynard_kinematics.bounds.width/2) {
      x = reynard_kinematics.bounds.x - reynard_kinematics.bounds.width/2;
    }
    if (y > (reynard_kinematics.bounds.y + reynard_kinematics.bounds.height/2)) {
      y = reynard_kinematics.bounds.y + reynard_kinematics.bounds.height/2;
    }
    if (y < reynard_kinematics.bounds.y-reynard_kinematics.bounds.height/2) {
      y = reynard_kinematics.bounds.y-reynard_kinematics.bounds.height/2;
    }

    let body_pos = paper.view.center.subtract(reynard_kinematics.body_offset).add(new paper.Point(x, -y));
    setBodyPosition(this.reynard_group, this.reynard_body, body_pos);

  }

  arm(q1, q2, q3) {
    if (q1 > reynard_kinematics.q1_bounds[1]) {
      q1 = reynard_kinematics.q1_bounds[1];
    }
    if (q1 < reynard_kinematics.q1_bounds[0]) {
      q1 = reynard_kinematics.q1_bounds[0];
    }
    if (q2 > reynard_kinematics.q2_bounds[1]) {
      q2 = reynard_kinematics.q2_bounds[1];
    }
    if (q2 < reynard_kinematics.q2_bounds[0]) {
      q2 = reynard_kinematics.q2_bounds[0];
    }
    if (q3 > reynard_kinematics.q3_bounds[1]) {
      q3 = reynard_kinematics.q3_bounds[1];
    }
    if (q3 < reynard_kinematics.q3_bounds[0]) {
      q3 = reynard_kinematics.q3_bounds[0];
    }
    setLinkPosition(this.reynard_body, this.reynard_link1, reynard_kinematics.p0, reynard_kinematics.p1_c, -q1);
    setLinkPosition(this.reynard_link1, this.reynard_link2, reynard_kinematics.p1_c, reynard_kinematics.p2_c, -q2);
    setLinkPosition(this.reynard_link2, this.reynard_tool, reynard_kinematics.p2_c, reynard_kinematics.p3_c, -q3);
  }

  changeColor(r, g, b) {
    let color = new paper.Color(r, g, b);
    let path12 = findChildByName(this.reynard_body, 'path1-2');
    path12.fillColor = color;
    let path13 = findChildByName(this.reynard_body, 'path1');
    path13.fillColor = color;
  }
}

async function loadSVGImage(group,url,position)
{
    let promise = new Promise(resolve => {
        options = {
            insert: true,
            onLoad: item => resolve(item)
        }
        group.importSVG(url, options);
    });
    let item = await promise;
    item.applyMatrix = false;
    if (position) {
        item.position=new paper.Point(position);
    }
    return item;
}

function setLinkPosition(parent,item,p1, p2, q)
{
    q_n = q + parent.rotation;
    item.position = parent.position.add(p1.rotate(parent.rotation).add(p2.rotate(q_n)));
    item.rotation = q_n;
}

function setBodyPosition(group,body,p)
{
    // Get global body position
    let offset = group.localToGlobal(body.position).subtract(group.position);
    group.position = p.subtract(offset);
}

function findChildByName(item, name) {
  if (item.name === name) {
      return item;
  }

  if (item.children) {
      for (let child of item.children) {
          let found = findChildByName(child, name);
          if (found) {
              return found;
          }
      }
  }

  return null;
}

window.onload = async function() {
    window.reynard = new ReynardRobot();
    await window.reynard.loadReynard();
}