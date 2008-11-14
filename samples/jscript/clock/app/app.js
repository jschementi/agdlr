Import("System.Windows.Application")
Import("System.Windows.Controls.Canvas")

Clock = function() {
	this.scene = Application.Current.LoadRootVisual(new Canvas, "app.xaml")
}
Clock.prototype = {
	start: function() {
		d = new Date()
		this.scene.hourAnimation.From    = this.fromAngle(d.getHours(), 1.0, d.getMinutes()/2.0)
	    this.scene.hourAnimation.To      = this.toAngle(d.getHours())
	    this.scene.minuteAnimation.From  = this.fromAngle(d.getMinutes())
	    this.scene.minuteAnimation.To    = this.toAngle(d.getMinutes())
	    this.scene.secondAnimation.From  = this.fromAngle(d.getSeconds())
	    this.scene.secondAnimation.To    = this.toAngle(d.getSeconds())
	},
	fromAngle: function(time, divisor, offset) {
		divisor = divisor == null ? 5.0 : divisor
		offset  = offset == null ? 0.0 : offset
		
		return ((time / (12.0 * divisor)) * 360.0) + offset + 180.0
	},
	toAngle: function(time) {
		return this.fromAngle(time) + 360.0
	}
}

clock = new Clock;
clock.start();