package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentComment extends Component
	{
		// Constructor
		public function ComponentComment(data:String = null, existingcontent:Object = null)
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
		public function get Comment():String
		{
			return super.flash_proxy::getProperty("comment");
		}
		public function set Comment(value:String):void
		{
			super.flash_proxy::setProperty("comment", value);
		}
		
		public function get CommentValidation():String
		{
			return super.flash_proxy::getProperty("commentvalidation");
		}

		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			return JSONDataString("comment", Comment, false);
		}

		// Type
		static public var TYPE:String = "COMMENT";

		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"COMMENT\"," +
			"\"id\":0," +
			"\"name\":\"Comment\"," +
			"\"comment\":\"\"}";
	}
}
