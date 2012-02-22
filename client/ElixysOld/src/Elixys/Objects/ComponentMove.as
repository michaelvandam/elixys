package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentMove extends Component
	{
		// Constructor
		public function ComponentMove(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			if ((data == null) && (existingcontent == null))
			{
				data = DEFAULT;
			}
			super(data, existingcontent);
			
			// Validate the object type
			if ((ComponentType != null) && (ComponentType != TYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Data wrappers
		public function get Reactor():uint
		{
			return super.flash_proxy::getProperty("reactor");
		}
		public function set Reactor(value:uint):void
		{
			super.flash_proxy::setProperty("reactor", value);
		}
		
		public function get ReactorValidation():String
		{
			return super.flash_proxy::getProperty("reactorvalidation");
		}

		public function get Position():String
		{
			return super.flash_proxy::getProperty("position");
		}
		public function set Position(value:String):void
		{
			super.flash_proxy::setProperty("position", value);
		}

		public function get PositionValidation():String
		{
			return super.flash_proxy::getProperty("positionvalidation");
		}

		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sMoveDetails:String = JSONDataObject("reactor", Reactor);
			sMoveDetails += JSONDataString("position", Position, false);
			return sMoveDetails;
		}

		// Type
		static public var TYPE:String = "MOVE";

		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"MOVE\"," +
			"\"id\":0," +
			"\"name\":\"Move\"," +
			"\"reactor\":0," +
			"\"position\":0}";
	}
}
